from lxml import etree

ns = etree.FunctionNamespace(None)


@ns
def lower(context, a):
    """lower-case() function for XPath 1.0"""
    return a.lower()


@ns
def tag(context):
    """:return str
    Returns tag without namespace. Just short replacement for xpath local-name() function
    without arguments"""
    ns_key = context.context_node.prefix
    ns_link = "{{{}}}".format(context.context_node.nsmap.get(ns_key))
    return context.context_node.tag.replace(ns_link, "")


@ns
def match(context, tag, *search):
    """:return bool
    search exact match for tag from several variants
    """
    return any(pattern == tag for pattern in search)