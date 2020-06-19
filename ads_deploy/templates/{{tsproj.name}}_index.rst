{% import "util.macro" as util %}
{% set sectionname %}{{tsproj.filename}} Documentation{% endset %}
{{ util.section(sectionname) }}

.. toctree::
    :maxdepth: 2
    :caption: Contents:

    {{ tsproj.name }}_summary
{% for plc in tsproj.plcs %}
    {{ tsproj.name }}_{{ plc.name }}_summary
    {{ tsproj.name }}_{{ plc.name }}_epics
    {{ tsproj.name }}_{{ plc.name }}_source
{% endfor %}


{{ util.section("Pragma Summary") }}

.. csv-table::
    :header: PLC Name, Total Pragmas, Errors
    :align: center

    {% for plc in tsproj.plcs %}
    :ref:`{{ plc.name }} <{{ plc.name }}_pragmas>`, {{ plc.pragma_count }}, {{ plc.pragma_errors }}
    {% endfor %}


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
