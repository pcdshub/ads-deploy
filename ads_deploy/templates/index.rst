{% import "util.macro" as util %}
{% set sectionname %}{{solution_name}} Documentation{% endset %}
{{ util.section(sectionname) }}

.. toctree::
    :maxdepth: 3
    :caption: Contents:

{% for tsproj in tsprojects %}
    {{ tsproj.name }}_index
{% endfor %}


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
