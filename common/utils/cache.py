from django.views.decorators.vary import vary_on_headers


def vary_on_headers_with_default(*headers: str):
    return vary_on_headers(*headers, "Accept-Language")
