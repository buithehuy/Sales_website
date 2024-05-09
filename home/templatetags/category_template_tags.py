from django import template
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.db.models import F, FloatField, ExpressionWrapper

from home.models import Category, Item

register = template.Library()

@register.filter(name='calculate_discount_percentage')
def calculate_discount_percentage(discount_price, price):
    if price == 0:
        return 0
    return round(((price - discount_price) / price) * 100, 2)

@register.simple_tag
def categories():
    items = Category.objects.filter(is_active=True).order_by('title')
    items_li = ""
    for i in items:
        items_li += """<li><a href="/category/{}">{}</a></li>""".format(i.slug, i.title)
    return mark_safe(items_li)

@register.simple_tag
def categories_mobile():
    items = Category.objects.filter(is_active=True).order_by('title')
    items_li = ""
    for i in items:
        items_li += """<li class="item-menu-mobile"><a href="/category/{}">{}</a></li>""".format(i.slug, i.title)
    return mark_safe(items_li)


@register.simple_tag
def categories_li_a():
    items = Category.objects.filter(is_active=True).order_by('title')
    items_li_a = ""
    for i in items:
        items_li_a += """<li class="p-t-4"><a href="/category/{}" class="s-text13">{}</a></li>""".format(i.slug,
                                                                                                         i.title)
    return mark_safe(items_li_a)


@register.simple_tag
def categories_div():
    """
    section banner
    :return:
    """
    items = Category.objects.filter(is_active=True).order_by('title')
    items_div = ""
    item_div_list = ""
    for i, j in enumerate(items):
        # if not i % 2:
        #     items_div += """<div class="block1 hov-img-zoom pos-relative m-b-30"><img src="/media/{}" alt="IMG-BENNER"><div class="block1-wrapbtn w-size2"><a href="/category/{}" class="flex-c-m size2 m-text2 bg9 hov1 trans-0-4">{}</a></div></div>""".format(
        #         j.image, j.slug, j.title)
        # else:
            items_div_ = """<div class="block1 hov-img-zoom pos-relative m-b-30"><img src="/media/{}" alt="IMG-BENNER"><div class="block1-wrapbtn w-size2"><a href="/category/{}" class="flex-c-m size2 m-text2 bg9 hov1 trans-0-4">{}</a></div></div>""".format(
                j.image, j.slug, j.title)
            item_div_list += """<div class=" m-r-0 m-l-0">""" + items_div + items_div_ + """</div>"""
            items_div = ""
            # col-sm-10 col-md-8 col-lg-4

    return mark_safe(item_div_list)


def render_item_block(item, show_discount=False):
    """
    Render HTML block for an item
    """
    discount_html = ""
    if show_discount and item.discount_price:
        discount_html = f"""
            <span class="block2-oldprice m-text7 p-r-5">${item.price}</span>
            <span class="block2-newprice m-text8 p-r-5">${item.discount_price}</span>
         
        """

    html = f"""
        <div class="col-sm-12 col-md-6 col-lg-4 p-b-50 ">
            <!-- Block2 -->
            <div class="block2 bgwhite wrap-pic-cir-5px">
                <a href="{reverse("product", kwargs={'slug': item.slug})}">
                    <div class="block2-img wrap-pic-w of-hidden pos-relative block2-labelnew">
                        <img src="/media/{item.image}" alt="IMG-PRODUCT" style="height: 360px;">
                        <div class="block2-overlay trans-0-4">
                            <a href="#" class="block2-btn-addwishlist hov-pointer trans-0-4">
                                <i class="icon-wishlist icon_heart_alt" aria-hidden="true"></i>
                                <i class="icon-wishlist icon_heart dis-none" aria-hidden="true"></i>
                            </a>
                            <div class="block2-btn-addcart w-size1 trans-0-4">
                                <a href="{reverse("product", kwargs={'slug': item.slug})}" class="flex-c-m size1 bg4 bo-rad-23 hov1 s-text1 trans-0-4">
                                    Add to Cart
                                </a>
                            </div>
                        </div>
                    </div>
                </a>
                <div class="block2-txt p-t-20">
                    <a href="{reverse("product", kwargs={'slug': item.slug})}" class="block2-name dis-block s-text3 p-b-5">{item.title}</a>
                    {discount_html}
                </div>
            </div>
        </div>
    """
    return html

@register.simple_tag
def items_div():
    """
    Render items as divs
    """
    items = Item.objects.filter(is_active=True).order_by('title')[:6]
    item_div_list = ""

    for item in items:
        item_div_list += render_item_block(item, show_discount=True)

    return mark_safe(item_div_list)

@register.simple_tag


def deepest_discount_items():
    """
    Render items with the deepest discounts
    """
    items = Item.objects.annotate(
        discount_ratio=ExpressionWrapper(F('discount_price') / F('price'), output_field=FloatField())
    ).filter(is_active=True, discount_price__isnull=False).order_by('-discount_ratio')[:6]

    item_div_list = ""

    for item in items:
        item_div_list += render_item_block(item, show_discount=True)

    return mark_safe(item_div_list)
