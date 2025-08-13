# credit_simulator/forms.py

from django import forms
from django.core.exceptions import ValidationError
from decimal import Decimal

from .models import CreditProduct
from .services import CreditSimulationService


class CreditProductForm(forms.ModelForm):
    """
    Formulario para crear y editar productos de crédito.
    Solo accesible para usuarios staff.
    """

    class Meta:
        model = CreditProduct
        fields = [
            'commercial_name',
            'internal_code',
            'description',
            'minimum_amount',
            'maximum_amount',
            'minimum_term_months',
            'maximum_term_months',
            'annual_interest_rate',
            'amortization_type',
            'has_life_insurance',
            'life_insurance_rate',
            'is_active'
        ]
        widgets = {
            'commercial_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Crédito de Consumo'
            }),
            'internal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: CC001'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del producto de crédito'
            }),
            'minimum_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '1.00'
            }),
            'maximum_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '1.00'
            }),
            'minimum_term_months': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'maximum_term_months': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'annual_interest_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'max': '99.99'
            }),
            'amortization_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'has_life_insurance': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'life_insurance_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.001',
                'min': '0.000',
                'max': '9.999'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Personalizar labels y help_text
        self.fields['commercial_name'].help_text = 'Nombre que verán los usuarios'
        self.fields['internal_code'].help_text = 'Código único interno (no se puede cambiar después)'
        self.fields['annual_interest_rate'].help_text = 'Tasa anual en porcentaje (ej: 15.50)'
        self.fields['life_insurance_rate'].help_text = 'Tasa mensual sobre saldo en porcentaje (ej: 0.500)'

    def clean_internal_code(self):
        """Valida que el código interno sea único solo en creación."""
        internal_code = self.cleaned_data.get('internal_code')

        if not internal_code:
            return internal_code

        # En edición, permitir el mismo código si es el mismo producto
        if self.instance and self.instance.pk:
            if self.instance.internal_code == internal_code:
                return internal_code

        # Verificar unicidad
        if CreditProduct.objects.filter(internal_code=internal_code).exists():
            raise ValidationError('Ya existe un producto con este código interno.')

        return internal_code

    def clean(self):
        """Validaciones cruzadas del formulario."""
        cleaned_data = super().clean()

        minimum_amount = cleaned_data.get('minimum_amount')
        maximum_amount = cleaned_data.get('maximum_amount')
        minimum_term = cleaned_data.get('minimum_term_months')
        maximum_term = cleaned_data.get('maximum_term_months')
        has_life_insurance = cleaned_data.get('has_life_insurance')
        life_insurance_rate = cleaned_data.get('life_insurance_rate')

        # Validar montos
        if minimum_amount and maximum_amount:
            if minimum_amount >= maximum_amount:
                raise ValidationError({
                    'maximum_amount': 'El monto máximo debe ser mayor al mínimo.'
                })

        # Validar plazos
        if minimum_term and maximum_term:
            if minimum_term >= maximum_term:
                raise ValidationError({
                    'maximum_term_months': 'El plazo máximo debe ser mayor al mínimo.'
                })

        # Validar seguro de desgravamen
        if has_life_insurance and not life_insurance_rate:
            raise ValidationError({
                'life_insurance_rate': 'Debe especificar la tasa del seguro cuando está habilitado.'
            })

        return cleaned_data

    def save(self, commit=True):
        """Guarda el producto asignando el usuario correspondiente."""
        instance = super().save(commit=False)

        if self.user:
            if not instance.pk:  # Nuevo producto
                instance.created_by = self.user
            else:  # Producto existente
                instance.updated_by = self.user

        if commit:
            instance.save()

        return instance


class CreditSimulationForm(forms.Form):
    """
    Formulario para realizar simulaciones de crédito.
    Accesible para usuarios normales.
    """

    credit_product = forms.ModelChoiceField(
        label='Producto de Crédito',
        queryset=CreditProduct.objects.active(),
        empty_label='Seleccione un producto',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_credit_product'
        }),
        help_text='Seleccione el tipo de crédito que desea simular'
    )

    requested_amount = forms.DecimalField(
        label='Monto solicitado',
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('1.00'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '1.00',
            'placeholder': '10000.00',
            'id': 'id_requested_amount'
        }),
        help_text='Ingrese el monto que desea solicitar'
    )

    term_months = forms.IntegerField(
        label='Plazo en meses',
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'placeholder': '12',
            'id': 'id_term_months'
        }),
        help_text='Ingrese el número de meses para pagar'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Si hay datos iniciales, configurar los límites dinámicamente
        if self.data:
            try:
                product_id = int(self.data.get('credit_product'))
                product = CreditProduct.objects.get(pk=product_id, is_active=True)
                self._set_field_limits(product)
            except (ValueError, TypeError, CreditProduct.DoesNotExist):
                pass

    def _set_field_limits(self, product: CreditProduct):
        """Configura los límites de los campos basado en el producto seleccionado."""
        # Actualizar límites del monto
        amount_widget = self.fields['requested_amount'].widget
        amount_widget.attrs.update({
            'min': str(product.minimum_amount),
            'max': str(product.maximum_amount)
        })

        # Actualizar límites del plazo
        term_widget = self.fields['term_months'].widget
        term_widget.attrs.update({
            'min': str(product.minimum_term_months),
            'max': str(product.maximum_term_months)
        })

        # Actualizar help_text con los límites
        self.fields['requested_amount'].help_text = (
            f'Monto entre ${product.minimum_amount:,.2f} y ${product.maximum_amount:,.2f}'
        )
        self.fields['term_months'].help_text = (
            f'Plazo entre {product.minimum_term_months} y {product.maximum_term_months} meses'
        )

    def clean(self):
        """Validaciones del formulario de simulación."""
        cleaned_data = super().clean()

        product = cleaned_data.get('credit_product')
        amount = cleaned_data.get('requested_amount')
        term_months = cleaned_data.get('term_months')

        if product and amount and term_months:
            try:
                # Usar el servicio para validar los parámetros
                CreditSimulationService.validate_simulation_parameters(
                    product, amount, term_months
                )
            except ValidationError as e:
                raise forms.ValidationError(str(e))

        return cleaned_data


class CreditProductFilterForm(forms.Form):
    """
    Formulario para filtrar productos de crédito en la vista de lista.
    """

    search = forms.CharField(
        label='Buscar',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre o código...'
        })
    )

    amortization_type = forms.ChoiceField(
        label='Tipo de amortización',
        choices=[('', 'Todos')] + CreditProduct.AMORTIZATION_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    is_active = forms.ChoiceField(
        label='Estado',
        choices=[
            ('', 'Todos'),
            ('true', 'Activos'),
            ('false', 'Inactivos')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    min_amount = forms.DecimalField(
        label='Monto mínimo desde',
        required=False,
        min_value=Decimal('0.01'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '1000.00'
        })
    )

    max_amount = forms.DecimalField(
        label='Monto máximo hasta',
        required=False,
        min_value=Decimal('0.01'),
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '50000.00'
        })
    )

    def clean(self):
        """Validar que el monto mínimo sea menor al máximo."""
        cleaned_data = super().clean()

        min_amount = cleaned_data.get('min_amount')
        max_amount = cleaned_data.get('max_amount')

        if min_amount and max_amount and min_amount >= max_amount:
            raise ValidationError('El monto mínimo debe ser menor al máximo.')

        return cleaned_data


class AmortizationScheduleForm(forms.Form):
    """
    Formulario simple para solicitar la generación de tabla de amortización.
    """

    simulation_id = forms.IntegerField(widget=forms.HiddenInput())

    def __init__(self, simulation, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.simulation = simulation
        self.fields['simulation_id'].initial = simulation.id

    def clean_simulation_id(self):
        """Valida que la simulación existe y pertenece al usuario."""
        simulation_id = self.cleaned_data.get('simulation_id')

        if simulation_id != self.simulation.id:
            raise ValidationError('ID de simulación no válido.')

        return simulation_id
