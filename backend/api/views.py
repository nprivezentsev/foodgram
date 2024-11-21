from io import BytesIO

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib import enums, pagesizes, styles
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)
from recipes.utils import generate_unique_short_link_code

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeShortReadSerializer,
    RecipeWriteSerializer,
    ShoppingCartSerializer,
    TagSerializer
)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)
    http_method_names = (
        'post', 'patch', 'get', 'delete', 'head', 'options'
    )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def add_to(self, request, pk, serializer_class, model_class):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = serializer_class(
            data={'recipe': recipe.id}, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            RecipeShortReadSerializer(
                recipe, context={'request': request}
            ).data,
            status=status.HTTP_201_CREATED
        )

    def remove_from(self, request, pk, model_class):
        recipe = get_object_or_404(Recipe, pk=pk)
        model_object = model_class.objects.filter(
            user=request.user,
            recipe=recipe
        )
        if model_object:
            model_object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(('get',), detail=True, url_path='get-link')
    def get_short_link(self, request, pk):
        recipe = self.get_object()
        if not recipe.short_link_code:
            recipe.short_link_code = generate_unique_short_link_code()
            recipe.save(update_fields=('short_link_code',))
        return Response({
            'short-link': request.build_absolute_uri(
                f'/s/{recipe.short_link_code}'
            )
        })

    @action(('post',), detail=True, url_path='shopping_cart')
    def add_to_cart(self, request, pk):
        return self.add_to(
            request, pk, ShoppingCartSerializer, ShoppingCart
        )

    @add_to_cart.mapping.delete
    def remove_from_cart(self, request, pk):
        return self.remove_from(request, pk, ShoppingCart)

    @action(('post',), detail=True, url_path='favorite')
    def add_to_favorite(self, request, pk):
        return self.add_to(request, pk, FavoriteSerializer, Favorite)

    @add_to_favorite.mapping.delete
    def remove_from_favorite(self, request, pk):
        return self.remove_from(request, pk, Favorite)

    @action(('get',), detail=False, url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=pagesizes.letter)
        # Регистрация шрифта.
        pdfmetrics.registerFont(
            TTFont(
                'OpenSans',
                settings.BASE_DIR / 'fonts/OpenSans-Regular.ttf'
            )
        )
        # Создание стилей для заголовка и текста.
        header_style = styles.ParagraphStyle(
            'HeaderStyle',
            fontName='OpenSans',
            fontSize=14,
            alignment=enums.TA_CENTER,
            spaceAfter=25
        )
        regular_style = styles.ParagraphStyle(
            'RegularStyle',
            fontName='OpenSans',
            fontSize=12,
            spaceAfter=10
        )
        # Запрос списка покупок пользователя.
        ingredients_summary = (
            RecipeIngredient.objects.filter(
                recipe__shoppingcart_users__user=request.user
            ).values(
                'ingredient__name', 'ingredient__measurement_unit'
            ).annotate(
                total_amount=Sum('amount')
            ).order_by(
                'ingredient__name'
            )
        )
        # Формирование заголовка и списка ингредиентов с буллетами.
        header = Paragraph('Список покупок', header_style)
        bullet_points = ListFlowable(
            [
                ListItem(
                    Paragraph(
                        f'{item["ingredient__name"]} — {item["total_amount"]} '
                        f'{item["ingredient__measurement_unit"]}',
                        regular_style
                    )
                )
                for item in ingredients_summary
            ],
            bulletType='bullet'
        )
        # Генерация и возврат PDF.
        doc.build([header, bullet_points])
        buffer.seek(0)
        return FileResponse(
            buffer,
            as_attachment=True,
            filename='shopping_cart.pdf'
        )


def redirect_to_recipe_detail(request, code):
    """
    Перенаправляет пользователя на детальную страницу рецепта по короткому
    коду. Короткий код (short_link_code) позволяет создавать компактные ссылки
    (например, https://example.com/s/abc123), которые можно использовать в
    email-рассылках, социальных сетях или других местах. После перехода по
    такой ссылке в юай происходит перенаправление на стандартный эндпоинт
    детального описания рецепта.
    """
    recipe = get_object_or_404(Recipe, short_link_code=code)
    return redirect(
        reverse(
            'api:recipes-detail',
            kwargs={'pk': recipe.id}
        ).replace('/api', '')
    )
