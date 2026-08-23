from django.shortcuts import get_object_or_404, render

from .models import Category, Product, ProductVariant


def _parse_size_guide(size_guide):
    rows = []
    for line in size_guide.splitlines():
        size, separator, label = line.partition('|')
        if separator and size.strip() and label.strip():
            rows.append({'size': size.strip(), 'label': label.strip()})
    return rows


def product_list(request):
    products = Product.objects.filter(is_active=True).select_related('category')

    category_slug = request.GET.get('category', '')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    context = {
        'products': products,
        'categories': Category.objects.all(),
        'selected_category': category_slug,
    }
    return render(request, 'products/list.html', context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    variants = list(product.variants.all())
    gallery_images = list(product.gallery_images.all())
    size_guide_rows = _parse_size_guide(product.size_guide)
    size_guide_labels = {row['size']: row['label'] for row in size_guide_rows}

    size_order = [code for code, _ in ProductVariant.Size.choices]
    size_display_map = dict(ProductVariant.Size.choices)
    sizes = sorted(
        {v.size for v in variants},
        key=lambda code: size_order.index(code),
    )
    colors = sorted({v.color for v in variants})

    context = {
        'product': product,
        'gallery_images': gallery_images,
        'sizes': [
            {
                'code': code,
                'display': f'{code} | {size_guide_labels[code]}' if code in size_guide_labels else size_display_map[code],
            }
            for code in sizes
        ],
        'size_guide_rows': size_guide_rows,
        'colors': colors,
        'variants_data': [
            {'id': v.id, 'size': v.size, 'color': v.color, 'stock': v.stock}
            for v in variants
        ],
    }
    return render(request, 'products/detail.html', context)
