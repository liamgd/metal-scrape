materials = [
    'Steel',
    'Galvanized Steel',
    'Aluminum 6061',
    'Aluminum 6063',
    'Stainless 304',
    'Stainless 316',
    'Brass 360',
    'Copper 110',
    'Cold Finish 1018',
    'Cold Finish 1045',
]

shapes = [
    'Angle',
    'Channel',
    'Beam',
    'Flat Bar',
    'Square Bar',
    'Round Bar',
    'Square Tube',
    'Rectangle Tube',
    'Round Tube',
    'Hexagon Bar',
]

URLS = {
    (
        'Steel',
        'Angle',
    ): 'https://www.metalsdepot.com/steel-products/steel-angle',
    (
        'Steel',
        'Channel',
    ): 'https://www.metalsdepot.com/steel-products/steel-channel',
    (
        'Steel',
        'Beam',
    ): 'https://www.metalsdepot.com/steel-products/steel-beams',
    (
        'Steel',
        'Flat Bar',
    ): 'https://www.metalsdepot.com/steel-products/steel-flat-bar',
    (
        'Steel',
        'Square Bar',
    ): 'https://www.metalsdepot.com/steel-products/steel-square-bar',
    (
        'Steel',
        'Round Bar',
    ): 'https://www.metalsdepot.com/steel-products/steel-round-bar',
    (
        'Steel',
        'Square Tube',
    ): 'https://www.metalsdepot.com/steel-products/steel-square-tube',
    (
        'Steel',
        'Rectangle Tube',
    ): 'https://www.metalsdepot.com/steel-products/steel-rectangle-tube',
    (
        'Steel',
        'Round Tube',
    ): 'https://www.metalsdepot.com/steel-products/steel-pipe',
    (
        'Aluminum 6061',
        'Angle',
    ): 'https://www.metalsdepot.com/aluminum-products/aluminum-angle-6061',
    (
        'Aluminum 6061',
        'Channel',
    ): 'https://www.metalsdepot.com/aluminum-products/aluminum-channel-6061',
    (
        'Aluminum 6061',
        'Beam',
    ): 'https://www.metalsdepot.com/aluminum-products/aluminum-beams',
    (
        'Aluminum 6061',
        'Flat Bar',
    ): 'https://www.metalsdepot.com/aluminum-products/aluminum-flat-bar',
    (
        'Aluminum 6061',
        'Square Bar',
    ): 'https://www.metalsdepot.com/aluminum-products/aluminum-square-bar',
    (
        'Aluminum 6061',
        'Round Bar',
    ): 'https://www.metalsdepot.com/aluminum-products/aluminum-round-bar',
    (
        'Aluminum 6061',
        'Square Tube',
    ): 'https://www.metalsdepot.com/aluminum-products/aluminum-square-tube',
    (
        'Aluminum 6061',
        'Rectangle Tube',
    ): 'https://www.metalsdepot.com/aluminum-products/aluminum-rectangle-tube',
    (
        'Aluminum 6061',
        'Round Tube',
    ): 'https://www.metalsdepot.com/aluminum-products/aluminum-round-tube',
    (
        'Aluminum 6063',
        'Angle',
    ): 'https://www.metalsdepot.com/aluminum-products/aluminum-angle-6063',
    (
        'Aluminum 6063',
        'Channel',
    ): 'https://www.metalsdepot.com/aluminum-products/aluminum-channel-6063',
    (
        'Stainless 304',
        'Angle',
    ): 'https://www.metalsdepot.com/stainless-steel-products/stainless-steel-angle',
    (
        'Stainless 304',
        'Channel',
    ): 'https://www.metalsdepot.com/stainless-steel-products/stainless-steel-channel',
    (
        'Stainless 304',
        'Flat Bar',
    ): 'https://www.metalsdepot.com/stainless-steel-products/stainless-steel-flat',
    (
        'Stainless 304',
        'Square Bar',
    ): 'https://www.metalsdepot.com/stainless-steel-products/stainless-steel-square',
    (
        'Stainless 304',
        'Round Bar',
    ): 'https://www.metalsdepot.com/stainless-steel-products/stainless-steel-round',
    (
        'Stainless 304',
        'Square Tube',
    ): 'https://www.metalsdepot.com/stainless-steel-products/stainless-steel-square-tube',
    (
        'Stainless 304',
        'Rectangle Tube',
    ): 'https://www.metalsdepot.com/stainless-steel-products/stainless-rectangle-tube',
    (
        'Stainless 304',
        'Round Tube',
    ): 'https://www.metalsdepot.com/stainless-steel-products/stainless-steel-round-tube',
    (
        'Stainless 316',
        'Angle',
    ): 'https://www.metalsdepot.com/stainless-steel-products/stainless-steel-angle-316-',
    (
        'Stainless 316',
        'Flat Bar',
    ): 'https://www.metalsdepot.com/stainless-steel-products/stainless-steel-flat-316-',
    (
        'Stainless 316',
        'Square Bar',
    ): 'https://www.metalsdepot.com/stainless-steel-products/stainless-steel-square-316-',
    (
        'Stainless 316',
        'Round Bar',
    ): 'https://www.metalsdepot.com/stainless-steel-products/stainless-steel-round-316-',
    (
        'Brass 360',
        'Rectangle Bar',
    ): 'https://www.metalsdepot.com/brass-products/brass-flat-bar',
    (
        'Brass 360',
        'Square Bar',
    ): 'https://www.metalsdepot.com/brass-products/brass-square-bar',
    (
        'Brass 360',
        'Round Bar',
    ): 'https://www.metalsdepot.com/brass-products/brass-round-bar',
    (
        'Copper 110',
        'Flat Bar',
    ): 'https://www.metalsdepot.com/brass-products/copper-flat-bar',
    (
        'Copper 110',
        'Square Bar',
    ): 'https://www.metalsdepot.com/brass-products/copper-square-bar',
    (
        'Copper 110',
        'Round Bar',
    ): 'https://www.metalsdepot.com/brass-products/copper-round-bar',
    (
        'Cold Finish 1018',
        'Flat Bar',
    ): 'https://www.metalsdepot.com/cold-finish-steel-products/cold-finish-steel-flat',
    (
        'Cold Finish 1018',
        'Round Bar',
    ): 'https://www.metalsdepot.com/cold-finish-steel-products/cold-finish-steel-round',
    (
        'Cold Finish 1018',
        'Square Bar',
    ): 'https://www.metalsdepot.com/cold-finish-steel-products/cold-finish-steel-square',
    (
        'Cold Finish 1018',
        'Hexagon Bar',
    ): 'https://www.metalsdepot.com/cold-finish-steel-products/cold-finish-steel-hexagon',
    (
        'Cold Finish 1045',
        'Round Bar',
    ): 'https://www.metalsdepot.com/cold-finish-steel-products/1045-tgp-steel-shafting',
}
