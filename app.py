import helperFunctions as hf

import flask
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from bokeh.palettes import viridis

import numpy as np

app = flask.Flask(__name__)

def getitem(obj, item, default):
    if item not in obj:
        return default
    else:
        return obj[item]

@app.route('/')
def opacity_wizard():

    args = flask.request.args
    met = float(getitem(args, 'met', 0.0))
    temp = int(getitem(args, 'temp', 1600))
    logp = float(getitem(args, 'logp', 1.5))

    abund_result = []
    ch4 = getitem(args, 'ch4', True)
    if ch4: abund_result.append('ch4')
    h2o = getitem(args, 'h2o', True)
    if h2o: abund_result.append('h2o')
    nh3 = getitem(args, 'nh3', True)
    if nh3: abund_result.append('nh3')
    co = getitem(args, 'co', True)
    if co: abund_result.append('co')
    co2 = getitem(args, 'co2', True)
    if co: abund_result.append('co')
    feh = getitem(args, 'feh', False)
    if feh: abund_result.append('feh')
    h2s = getitem(args, 'h2s', True)
    if h2s: abund_result.append('h2s')
    ph3 = getitem(args, 'ph3', True)
    if ph3: abund_result.append('ph3')
    tio = getitem(args, 'tio', False)
    if tio: abund_result.append('tio')
    vo = getitem(args, 'vo', False)
    if vo: abund_result.append('vo')

    fig = figure(plot_width=1000, plot_height=450, responsive=False, y_axis_type="log", x_axis_type="log",
        y_range=[1e-35, 1e-18], x_range=[0.8, 20])

    if args:
        opac_kwargs = {'log_pressure_layer': logp, 'temp_layer': temp}
        
        color_list = viridis(len(abund_result))
        opac_result = hf.getPT(**opac_kwargs)
        wl,op = hf.getOpacity(filenumber=1)
        op_array = np.zeros((4,len(op)))
        leg_dict = { 'h2o':'H$_2$O', 'ch4':'CH$_4$', 'co':'CO', 'nh3':'NH3', 'n2':'N$_2$', 'ph3':'PH$_3$',  'h2s':'H$_2$S', 'tio':'TiO',
                    'vo':'VO', 'feh':'FeH', 'crh':'CrH', 'na':'Na', 'k':'K', 'rb':'Rb', 'cs':'Cs', 'co2':'CO$_2$'}
        for j in range(len(abund_result)):
         #   print abund_result[j]
            for i in range(len(opac_result)):
                ii = opac_result[i]+1
                wl,op_array[i] = hf.getOpacity(filenumber=ii, molname=abund_result[j])
            op = hf.interpolateOpacityFiles(10.0**opac_kwargs['log_pressure_layer'], opac_kwargs['temp_layer'], opac_result, op_array)
            abunds = hf.getAbundances(10.0**opac_kwargs['log_pressure_layer'], opac_kwargs['temp_layer'], [abund_result[j]], metallicity=str(met))
            fig.line(wl, op*abunds[0], color=color_list[j], legend=leg_dict[abund_result[j]])

        fig.legend.location = "top_left"
        fig.legend.orientation = "horizontal"

    fig.xaxis.axis_label = 'Wavelength (um)'
    fig.yaxis.axis_label = 'opacity x mixing ratio (cm2 / molecule)'

    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    script, div = components(fig)

    html = flask.render_template('embed.html',
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources,
        met=met,
        temp=temp,
        logp=logp,
        ch4=ch4,
        h2o=h2o,
        nh3=nh3,
        co=co,
        co2=co2,
        feh=feh,
        h2s=h2s,
        ph3=ph3,
        tio=tio,
        vo=vo)

    return encode_utf8(html)

if __name__ == '__main__':
    app.run()
