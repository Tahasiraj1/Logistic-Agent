
tile = 'OpenStreetMap'

def set_tile(style: str):
    global tile
    tile = style

def get_tile():
    return tile

tile_providers = {
    "OpenStreetMap": {
        "tiles": "OpenStreetMap",
        "attr": None
    },
    "CartoDB Positron": {
        "tiles": "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        "attr": "© OpenStreetMap contributors, © CartoDB"
    },
    "CartoDB Dark Matter": {
        "tiles": "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        "attr": "© OpenStreetMap contributors, © CartoDB"
    },
    "Thunderforest SpinalMap": {
        "tiles": 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        "attr": 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
    },
    'Esri.NatGeoWorldMap': {
        'tiles': 'https://server.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}', 
	    'attr': 'Tiles &copy; Esri &mdash; National Geographic, Esri, DeLorme, NAVTEQ, UNEP-WCMC, USGS, NASA, ESA, METI, NRCAN, GEBCO, NOAA, iPC',
    },
    'MtbMap': {
        'tiles': 'http://tile.mtbmap.cz/mtbmap_tiles/{z}/{x}/{y}.png',
        'attr': '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &amp; USGS'
    }
}
