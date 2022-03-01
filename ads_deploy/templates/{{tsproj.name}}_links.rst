{% import "util.macro" as util %}

{{ util.section("Links") }}

.. csv-table::
    :header: Owner A, Item A, Owner B, Item B
    :align: center

    {% for link in get_links(tsproj.obj) | sort(attribute="a") %}
        {{ link.a[0] }}, {{ link.a[1] }}, {{ link.b[0] }}, {{ link.b[1] }}
    {% endfor %}{# for link... #}
