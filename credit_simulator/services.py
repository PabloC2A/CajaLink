# credit_simulator/services.py

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Tuple, Optional
import math

from django.core.exceptions import ValidationError
from .models import CreditProduct, CreditSimulation, AmortizationScheduleEntry


class CreditCalculationError(Exception):
    """Excepción personalizada para errores en cálculos de crédito."""
    pass


class CreditSimulationService:
    """
    Servicio que maneja todos los cálculos relacionados con simulaciones de crédito.
    Implementa los diferentes sistemas de amortización disponibles.
    """

    # Constantes para precisión de cálculos
    DECIMAL_PLACES = 2
    CALCULATION_PRECISION = 8  # Precisión interna para cálculos

    @classmethod
    def validate_simulation_parameters(
            cls,
            credit_product: CreditProduct,
            amount: Decimal,
            term_months: int
    ) -> None:
        """
        Valida que los parámetros de simulación estén dentro de los límites
        del producto de crédito.
        """
        if not credit_product.is_active:
            raise ValidationError("El producto de crédito no está activo.")

        if not credit_product.is_amount_valid(amount):
            raise ValidationError(
                f"El monto debe estar entre ${credit_product.minimum_amount:,.2f} "
                f"y ${credit_product.maximum_amount:,.2f}"
            )

        if not credit_product.is_term_valid(term_months):
            raise ValidationError(
                f"El plazo debe estar entre {credit_product.minimum_term_months} "
                f"y {credit_product.maximum_term_months} meses"
            )

    @classmethod
    def calculate_simulation(
            cls,
            credit_product: CreditProduct,
            amount: Decimal,
            term_months: int,
            user=None,
            ip_address: str = None
    ) -> CreditSimulation:
        """
        Realiza una simulación completa de crédito y retorna el objeto simulación.
        """
        # Validar parámetros
        cls.validate_simulation_parameters(credit_product, amount, term_months)

        # Obtener calculadora según tipo de amortización
        calculator = cls._get_calculator(credit_product.amortization_type)

        # Realizar cálculos
        calculation_result = calculator.calculate(credit_product, amount, term_months)

        # Crear y guardar simulación
        simulation = CreditSimulation.objects.create(
            credit_product=credit_product,
            user=user,
            requested_amount=amount,
            term_months=term_months,
            monthly_payment=calculation_result['monthly_payment'],
            total_interest=calculation_result['total_interest'],
            total_life_insurance=calculation_result['total_life_insurance'],
            total_amount=calculation_result['total_amount'],
            ip_address=ip_address
        )

        return simulation

    @classmethod
    def generate_amortization_schedule(
            cls,
            simulation: CreditSimulation
    ) -> List[AmortizationScheduleEntry]:
        """
        Genera la tabla de amortización completa para una simulación.
        """
        # Eliminar entradas existentes si las hay
        simulation.amortization_entries.all().delete()

        # Obtener calculadora
        calculator = cls._get_calculator(simulation.credit_product.amortization_type)

        # Generar tabla de amortización
        schedule_data = calculator.generate_schedule(
            simulation.credit_product,
            simulation.requested_amount,
            simulation.term_months
        )

        # Crear entradas en la base de datos
        entries = []
        for entry_data in schedule_data:
            entry = AmortizationScheduleEntry(
                simulation=simulation,
                installment_number=entry_data['installment_number'],
                principal_payment=entry_data['principal_payment'],
                interest_payment=entry_data['interest_payment'],
                life_insurance_payment=entry_data['life_insurance_payment'],
                total_payment=entry_data['total_payment'],
                remaining_balance=entry_data['remaining_balance']
            )
            entries.append(entry)

        # Guardar en lote para eficiencia
        AmortizationScheduleEntry.objects.bulk_create(entries)

        return entries

    @classmethod
    def _get_calculator(cls, amortization_type: str) -> 'BaseAmortizationCalculator':
        """Retorna la calculadora apropiada según el tipo de amortización."""
        calculators = {
            'FRENCH': FrenchAmortizationCalculator,
            'GERMAN': GermanAmortizationCalculator,
        }

        calculator_class = calculators.get(amortization_type)
        if not calculator_class:
            raise CreditCalculationError(f"Tipo de amortización no soportado: {amortization_type}")

        return calculator_class()


class BaseAmortizationCalculator:
    """Clase base abstracta para calculadoras de amortización."""

    def calculate(
            self,
            credit_product: CreditProduct,
            amount: Decimal,
            term_months: int
    ) -> Dict[str, Decimal]:
        """Metodo abstracto para calcular totales de la simulación."""
        raise NotImplementedError("Subclases deben implementar este método")

    def generate_schedule(
            self,
            credit_product: CreditProduct,
            amount: Decimal,
            term_months: int
    ) -> List[Dict]:
        """Metodo abstracto para generar tabla de amortización."""
        raise NotImplementedError("Subclases deben implementar este método")

    def _round_currency(self, value: Decimal) -> Decimal:
        """Redondea un valor a 2 decimales usando redondeo bancario."""
        return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def _calculate_life_insurance(
            self,
            balance: Decimal,
            insurance_rate: Decimal
    ) -> Decimal:
        """Calcula el seguro de desgravamen sobre el saldo."""
        if insurance_rate <= 0:
            return Decimal('0.00')

        # Seguro = saldo * tasa_mensual / 100
        insurance = balance * insurance_rate / Decimal('100')
        return self._round_currency(insurance)


class FrenchAmortizationCalculator(BaseAmortizationCalculator):
    """
    Calculadora para sistema de amortización francés (cuota fija).

    Características:
    - Cuota mensual constante
    - Interés calculado sobre saldo pendiente
    - Capital amortizado creciente
    """

    def calculate(
            self,
            credit_product: CreditProduct,
            amount: Decimal,
            term_months: int
    ) -> Dict[str, Decimal]:

        monthly_rate = credit_product.monthly_interest_rate

        # Calcular cuota mensual usando fórmula de anualidad
        if monthly_rate == 0:
            # Sin interés, cuota es simplemente capital / plazo
            monthly_payment = self._round_currency(amount / term_months)
        else:
            # Fórmula: PMT = PV * [r(1+r)^n] / [(1+r)^n - 1]
            factor = (1 + monthly_rate) ** term_months
            monthly_payment = amount * (monthly_rate * factor) / (factor - 1)
            monthly_payment = self._round_currency(monthly_payment)

        # Calcular totales
        total_payments = monthly_payment * term_months
        total_interest = total_payments - amount

        # Calcular seguro de desgravamen total (aproximado)
        total_life_insurance = Decimal('0.00')
        if credit_product.has_life_insurance:
            # Aproximación: promedio del saldo * tasa * meses
            avg_balance = amount / Decimal('2')
            monthly_insurance = self._calculate_life_insurance(
                avg_balance,
                credit_product.life_insurance_rate
            )
            total_life_insurance = monthly_insurance * term_months

        total_amount = total_payments + total_life_insurance

        return {
            'monthly_payment': monthly_payment,
            'total_interest': self._round_currency(total_interest),
            'total_life_insurance': total_life_insurance,
            'total_amount': self._round_currency(total_amount)
        }

    def generate_schedule(
            self,
            credit_product: CreditProduct,
            amount: Decimal,
            term_months: int
    ) -> List[Dict]:

        schedule = []
        balance = amount
        monthly_rate = credit_product.monthly_interest_rate

        # Calcular cuota fija
        calculation_result = self.calculate(credit_product, amount, term_months)
        base_monthly_payment = calculation_result['monthly_payment']

        for month in range(1, term_months + 1):
            # Calcular interés del mes
            interest_payment = self._round_currency(balance * monthly_rate)

            # Calcular pago a capital
            principal_payment = base_monthly_payment - interest_payment

            # Ajustar última cuota si hay diferencias por redondeo
            if month == term_months:
                principal_payment = balance
                base_monthly_payment = interest_payment + principal_payment

            principal_payment = self._round_currency(principal_payment)

            # Calcular seguro de desgravamen
            life_insurance = Decimal('0.00')
            if credit_product.has_life_insurance:
                life_insurance = self._calculate_life_insurance(
                    balance,
                    credit_product.life_insurance_rate
                )

            # Calcular totales
            total_payment = base_monthly_payment + life_insurance
            balance -= principal_payment
            balance = max(balance, Decimal('0.00'))  # Evitar saldos negativos por redondeo

            schedule.append({
                'installment_number': month,
                'principal_payment': principal_payment,
                'interest_payment': interest_payment,
                'life_insurance_payment': life_insurance,
                'total_payment': self._round_currency(total_payment),
                'remaining_balance': self._round_currency(balance)
            })

        return schedule


class GermanAmortizationCalculator(BaseAmortizationCalculator):
    """
    Calculadora para sistema de amortización alemán (capital fijo).

    Características:
    - Capital amortizado constante
    - Interés calculado sobre saldo pendiente
    - Cuota mensual decreciente
    """

    def calculate(
            self,
            credit_product: CreditProduct,
            amount: Decimal,
            term_months: int
    ) -> Dict[str, Decimal]:

        monthly_rate = credit_product.monthly_interest_rate

        # Capital fijo por cuota
        fixed_principal = self._round_currency(amount / term_months)

        # Calcular interés total (suma de intereses mensuales)
        total_interest = Decimal('0.00')
        balance = amount

        for month in range(term_months):
            interest_payment = self._round_currency(balance * monthly_rate)
            total_interest += interest_payment
            balance -= fixed_principal

        # Primera cuota (la más alta)
        first_interest = self._round_currency(amount * monthly_rate)
        monthly_payment = fixed_principal + first_interest

        # Calcular seguro de desgravamen total
        total_life_insurance = Decimal('0.00')
        if credit_product.has_life_insurance:
            balance = amount
            for month in range(term_months):
                insurance = self._calculate_life_insurance(
                    balance,
                    credit_product.life_insurance_rate
                )
                total_life_insurance += insurance
                balance -= fixed_principal

        total_amount = amount + total_interest + total_life_insurance

        return {
            'monthly_payment': monthly_payment,  # Primera cuota
            'total_interest': total_interest,
            'total_life_insurance': total_life_insurance,
            'total_amount': self._round_currency(total_amount)
        }

    def generate_schedule(
            self,
            credit_product: CreditProduct,
            amount: Decimal,
            term_months: int
    ) -> List[Dict]:

        schedule = []
        balance = amount
        monthly_rate = credit_product.monthly_interest_rate

        # Capital fijo por cuota
        fixed_principal = self._round_currency(amount / term_months)

        for month in range(1, term_months + 1):
            # Calcular interés del mes
            interest_payment = self._round_currency(balance * monthly_rate)

            # Capital fijo (ajustar en última cuota si es necesario)
            principal_payment = fixed_principal
            if month == term_months:
                principal_payment = balance  # Asegurar que se liquide completamente
                principal_payment = self._round_currency(principal_payment)

            # Calcular seguro de desgravamen
            life_insurance = Decimal('0.00')
            if credit_product.has_life_insurance:
                life_insurance = self._calculate_life_insurance(
                    balance,
                    credit_product.life_insurance_rate
                )

            # Calcular totales
            total_payment = principal_payment + interest_payment + life_insurance
            balance -= principal_payment
            balance = max(balance, Decimal('0.00'))  # Evitar saldos negativos

            schedule.append({
                'installment_number': month,
                'principal_payment': principal_payment,
                'interest_payment': interest_payment,
                'life_insurance_payment': life_insurance,
                'total_payment': self._round_currency(total_payment),
                'remaining_balance': self._round_currency(balance)
            })

        return schedule


class CreditProductService:
    """Servicio para gestión de productos de crédito (funciones administrativas)."""

    @staticmethod
    def create_credit_product(
            user,
            commercial_name: str,
            internal_code: str,
            minimum_amount: Decimal,
            maximum_amount: Decimal,
            minimum_term_months: int,
            maximum_term_months: int,
            annual_interest_rate: Decimal,
            amortization_type: str = 'FRENCH',
            has_life_insurance: bool = True,
            life_insurance_rate: Decimal = Decimal('0.500'),
            description: str = '',
            is_active: bool = True
    ) -> CreditProduct:
        """
        Crea un nuevo producto de crédito con validaciones completas.
        """
        product = CreditProduct(
            commercial_name=commercial_name,
            internal_code=internal_code,
            description=description,
            minimum_amount=minimum_amount,
            maximum_amount=maximum_amount,
            minimum_term_months=minimum_term_months,
            maximum_term_months=maximum_term_months,
            annual_interest_rate=annual_interest_rate,
            amortization_type=amortization_type,
            has_life_insurance=has_life_insurance,
            life_insurance_rate=life_insurance_rate if has_life_insurance else Decimal('0.000'),
            is_active=is_active,
            created_by=user
        )

        # Ejecutar validaciones del modelo
        product.full_clean()
        product.save()

        return product

    @staticmethod
    def update_credit_product(
            product: CreditProduct,
            user,
            **update_fields
    ) -> CreditProduct:
        """
        Actualiza un producto de crédito existente.
        """
        for field, value in update_fields.items():
            if hasattr(product, field):
                setattr(product, field, value)

        product.updated_by = user

        # Ejecutar validaciones
        product.full_clean()
        product.save()

        return product

    @staticmethod
    def get_available_products_for_amount(amount: Decimal) -> List[CreditProduct]:
        """
        Retorna los productos disponibles para un monto específico.
        """
        return list(CreditProduct.objects.for_amount(amount))

    @staticmethod
    def deactivate_product(product: CreditProduct, user) -> None:
        """
        Desactiva un producto de crédito.
        """
        product.is_active = False
        product.updated_by = user
        product.save(update_fields=['is_active', 'updated_by', 'updated_at'])
