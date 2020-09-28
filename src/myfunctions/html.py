import pandas as pd
import json
def pivot_cht_ui_body(index, pkldf, url="",
                      width="100%", height="500", **kwargs):
    df = pkldf.df
    json_kwargs = pkldf._attributes

    class _DataFrame(pd.DataFrame):
        def to_csv(self, **kwargs):
            return super().to_csv(**kwargs).replace("\r\n", "\n")
    df = _DataFrame(df)
    csv = df.to_csv(encoding='utf8')
    if hasattr(csv, 'decode'):
        csv = csv.decode('utf8')
    return make_pvt_html_body(index, pkldf._tag, csv, kwargs, json_kwargs)

def make_pvt_html_body(index, name, csv, kwargs, json_kwargs):
    return f"""
        <div class="widthy panel-group" id="accordion">
            <div class="widthy panel panel-default">
                <div class="widthy panel-heading">
                    <h4 class="widthy panel-title">
                  <a class="widthy accordion-toggle" data-toggle="collapse" data-parent="#accordion" href="#collapse{index}">{name}</a>
                </h4> </div>
                <div id="collapse{index}" class="divIFrame panel-collapse collapse in">
                    <div class="panel-body">
                        <iframe class='iframeStyle' srcdoc='<html><head><meta charset="UTF-8"><title>Configurator</title><link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/c3/0.4.11/c3.min.css"><script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.5/d3.min.js"></script><script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/c3/0.4.11/c3.min.js"></script><script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jquery/1.11.2/jquery.min.js"></script><script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jqueryui/1.11.4/jquery-ui.min.js"></script><script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jquery-csv/0.71/jquery.csv-0.71.min.js"></script><link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/pivottable/2.19.0/pivot.min.css"><script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/pivottable/2.19.0/pivot.min.js"></script><script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/pivottable/2.19.0/d3_renderers.min.js"></script><script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/pivottable/2.19.0/c3_renderers.min.js"></script><script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/pivottable/2.19.0/export_renderers.min.js"></script><style>div#expand{{display:block}}body{{font-family:Verdana}}.node{{border:solid 1px #fff;font:10px sans-serif;line-height:12px;overflow:hidden;position:absolute;text-indent:2px}}.c3-focused,.c3-line{{stroke-width:3px!important}}.c3-bar{{stroke:#fff!important;stroke-width:1}}.c3 text{{font-size:12px;color:grey}}.tick line{{stroke:#fff}}.c3-axis path{{stroke:grey}}.c3-circle{{opacity:1!important}}.c3-xgrid-focus{{visibility:hidden!important}}</style></head><body>
                        <script type="text/javascript">
                        $(function(){{
                        $("#output{index}").pivotUI(
                        $.csv.toArrays($("#output{index}").text())
                        , $.extend({{
                        renderers: $.extend(
                        $.pivotUtilities.renderers,
                        $.pivotUtilities.c3_renderers,
                        $.pivotUtilities.d3_renderers,
                        $.pivotUtilities.export_renderers
                        ),
                        hiddenAttributes: [""]
                        }}
                        , {{
                        onRefresh: function(config) {{
                        var config_copy = JSON.parse(JSON.stringify(config));
                        //delete some values which are functions
                        delete config_copy["aggregators"];
                        delete config_copy["renderers"];
                        //delete some bulky default values
                        delete config_copy["rendererOptions"];
                        delete config_copy["localeStrings"];
                        $("#copy{index}").text(JSON.stringify(config_copy, undefined, 2));
                        }}
                        }}
                        , {json.dumps(kwargs)}
                        ,
                        {json_kwargs}
                        )
                        ).show();
                        }});
                        </script>
                        <div id="output{index}" style="display: none;">{csv}</div>
                        <textarea id="copy{index}"
                        style="float: left; width: 0px; height: 0px; margin: 0px; opacity:0;" readonly>
                        </textarea>
                        <button onclick="copyTextFunction()">Copy settings</button>
                        <script>
                        function copyTextFunction() {{
                        var copyText = document.getElementById("copy{index}");
                        copyText.select();
                        document.execCommand("copy");
                        }}
                        </script>
                        </body></html>'> </iframe>
                    </div>
                </div>
            </div>
        </div>

"""