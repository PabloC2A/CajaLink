# staffpanel/selectors.py

from django.db.models import Q, Case, When, Value, BooleanField, CharField, IntegerField, QuerySet
from legacy_models.models import Socio


def get_unified_socio_list(search_query: str = '') -> 'QuerySet[Socio]':
    """
    Selector que obtiene una lista unificada de socios con información de vinculación.

    Implementa:
    - Single Responsibility: Solo se encarga de construir la consulta
    - DRY: Centraliza la lógica de consulta unificada
    - High Cohesion: Agrupa toda la lógica relacionada con la consulta

    Args:
        search_query: Término de búsqueda opcional

    Returns:
        QuerySet de Socio anotado con información de vinculación
    """
    # Base queryset con optimización usando select_related
    queryset = Socio.objects.select_related('usersociolink__user')

    # Aplicar filtro de búsqueda si existe (KISS principle)
    if search_query:
        search_filter = (
                Q(nombres__icontains=search_query) |
                Q(apellidos__icontains=search_query) |
                Q(cedula__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(usersociolink__user__username__icontains=search_query) |
                Q(usersociolink__user__email__icontains=search_query)
        )
        queryset = queryset.filter(search_filter)

    # Anotar información de vinculación usando Case/When (evita múltiples queries)
    queryset = queryset.annotate(
        is_linked=Case(
            When(usersociolink__isnull=False, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        ),
        web_username=Case(
            When(
                usersociolink__isnull=False,
                then='usersociolink__user__username'
            ),
            default=Value(''),
            output_field=CharField()
        ),
        web_email=Case(
            When(
                usersociolink__isnull=False,
                then='usersociolink__user__email'
            ),
            default=Value(''),
            output_field=CharField()
        ),
        web_is_active=Case(
            When(
                usersociolink__isnull=False,
                then='usersociolink__user__is_active'
            ),
            default=Value(False),
            output_field=BooleanField()
        ),
        user_id=Case(
            When(
                usersociolink__isnull=False,
                then='usersociolink__user__id'
            ),
            default=Value(None),
            output_field=IntegerField()
        )
    )

    # Ordenar: vinculados primero, luego por apellidos (UX mejorada)
    return queryset.order_by('-is_linked', 'apellidos', 'nombres')
