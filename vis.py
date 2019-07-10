from pyecharts import options as opts
from pyecharts.charts import BMap
from pyecharts.globals import BMapType, ChartType, GeoType
from gen_pickle import load_street_pickle
from speed import read_speed, read_pred_speed
from numpy import mean, isnan


def prepare_coord(info):
    coord = {}
    for street in info:
        long = mean([x['long'] for x in info[street]])
        lat = mean([x['lat'] for x in info[street]])
        coord[street] = [long, lat]
    return coord


def get_data_pair(speed, n):
    data = []
    for street in speed:
        spd = speed[street][n]
        if isnan(spd):
            spd = 0
        data.append(
            [street, spd]
        )
    return data


if __name__ == '__main__':
    info = load_street_pickle()
    m = BMap(init_opts=opts.InitOpts(width="1600px", height="800px"))
    m.add_schema(
        baidu_ak="Uf1rIjuIVVXxDwEy0iEU0tApwdoqGeGn",
        center=[108.953457, 34.26949],
        zoom=15,
        is_roam=True,
        map_style={
            "styleJson": [
                {"featureType": "water", "elementType": "all", "stylers": {"color": "#d1d1d1"}},
                {"featureType": "land", "elementType": "all", "stylers": {"color": "#f3f3f3"}},
                {"featureType": "railway", "elementType": "all", "stylers": {"visibility": "off"}},
                {"featureType": "highway", "elementType": "all", "stylers": {"color": "#fdfdfd"}},
                {"featureType": "highway", "elementType": "labels", "stylers": {"visibility": "off"}},
                {"featureType": "arterial", "elementType": "geometry", "stylers": {"color": "#fefefe"}},
                {"featureType": "arterial", "elementType": "geometry.fill", "stylers": {"color": "#fefefe"}},
                {"featureType": "poi", "elementType": "all", "stylers": {"visibility": "on"}},
                {"featureType": "green", "elementType": "all", "stylers": {"visibility": "off"}},
                {"featureType": "subway", "elementType": "all", "stylers": {"visibility": "off"}},
                {"featureType": "manmade", "elementType": "all", "stylers": {"color": "#d1d1d1"}},
                {"featureType": "local", "elementType": "all", "stylers": {"color": "#d1d1d1"}},
                {"featureType": "arterial", "elementType": "labels", "stylers": {"visibility": "on"}},
                {"featureType": "boundary", "elementType": "all", "stylers": {"color": "#fefefe"}},
                {"featureType": "building", "elementType": "all", "stylers": {"color": "#d1d1d1"}},
                {"featureType": "label", "elementType": "labels.text.fill", "stylers": {"color": "#999999"}}
            ]
        }
    )
    coord = prepare_coord(load_street_pickle())
    for s, (long, lat) in coord.items():
        m.add_coordinate(s, long, lat)
    speed, n_slice = read_speed()
    # Match T-GCN expand 3 times... (don't know why)
    idx_map = list(range(0, 114 - 12 - 3 - 1)) + list(range(114, 143 - 12 - 3))
    pred_speed, n_slice1 = read_pred_speed()
    assert len(idx_map) == n_slice1
    m.add(
        series_name="actual",
        type_="heatmap",
        data_pair=get_data_pair(speed, 0)
    ).add(
        series_name="predict",
        type_="heatmap",
        data_pair=get_data_pair(pred_speed, 0),
    ).add_control_panel(
        copyright_control_opts=opts.BMapCopyrightTypeOpts(position=3),
        maptype_control_opts=opts.BMapTypeControlOpts(type_=BMapType.MAPTYPE_CONTROL_DROPDOWN),
        scale_control_opts=opts.BMapScaleControlOpts(),
        overview_map_opts=opts.BMapOverviewMapControlOpts(is_open=True),
        navigation_control_opts=opts.BMapNavigationControlOpts(),
        geo_location_control_opts=opts.BMapGeoLocationControlOpts(),
    ).set_global_opts(
        visualmap_opts=opts.VisualMapOpts(
            min_=0,
            max_=60,
            range_color=['blue', 'blue', 'green', 'yellow', 'red']
        ),
        title_opts=opts.TitleOpts(title="Traffic Status of Xi'An")
    )
    m.render('test.html')
