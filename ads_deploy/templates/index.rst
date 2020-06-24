{% import "util.macro" as util %}
{% set sectionname %}{{solution_name}}{% endset %}
{{ util.section(sectionname) }}

{% for tsproj in tsprojects %}
.. toctree::
    :maxdepth: 2
    :caption: {{ tsproj.name }}

    {{ tsproj.name }}_pragmas
    {{ tsproj.name }}_nc
    {{ tsproj.name }}_boxes
    {{ tsproj.name }}_links

{% for plc in tsproj.plcs %}

.. toctree::
    :maxdepth: 2
    :caption: {{ plc.name }}

    {{ tsproj.name }}_{{ plc.name }}_summary
    {{ tsproj.name }}_{{ plc.name }}_epics
    {{ tsproj.name }}_{{ plc.name }}_source
{% endfor %}

{% endfor %}


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
