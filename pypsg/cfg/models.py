"""
A module to store PSG config models.
"""
from astropy import units as u
from astropy.units import cds
from astropy.units import imperial



from pypsg import units as u_psg

from pypsg.cfg.base import Model
from pypsg.cfg.base import CharField, IntegerField, DateField
from pypsg.cfg.base import FloatField, QuantityField, CodedQuantityField, CharChoicesField
from pypsg.cfg.base import GeometryOffsetField, GeometryUserParamField, MoleculesField, AerosolsField
from pypsg.cfg.base import ProfileField, BooleanField


class Target(Model):
    """
    PSG parameter model for keywords begining with `OBJECT`.
    """
    object = CharChoicesField('object',('Exoplanet','Planet','Asteroid','Moon','Comet','Object'),max_length=50)
    name = CharField('object-name',max_length=50)
    date = DateField('object-date')
    diameter = QuantityField('object-diameter',u.km)
    gravity = CodedQuantityField(
        allowed_units=(u.Unit('m s-2'),u.Unit('g cm-3'), u.kg),
        unit_codes=('g', 'rho', 'kg'),
        fmt=('.4f','.4f','.4e'),
        names=('object-gravity','object-gravity-unit')
    )
    star_distance = QuantityField('object-star-distance',u.AU)
    star_velocity = QuantityField('object-star-velocity',u.Unit('km s-1'))
    solar_longitude = QuantityField('object-solar-longitude',u.deg)
    solar_latitude = QuantityField('object-solar-latitude',u.deg)
    season = QuantityField('object-season',u.deg)
    inclination = QuantityField('object-inclination',u.deg)
    position_angle = QuantityField('object-position-angle',u.deg)
    star_type = CharChoicesField('object-star-type',('O','B','A','F','G','K','M',''),max_length=1)
    star_temperature = QuantityField('object-star-temperature',u.K)
    star_radius = QuantityField('object-star-radius',u.R_sun)
    star_metallicity = FloatField('object-star-metallicity')
    obs_longitude = QuantityField('object-obs-longitude',u.deg)
    obs_latitude = QuantityField('object-obs-latitude',u.deg)
    obs_velocity = QuantityField('object-obs-velocity',u.Unit('km s-1'))
    period = QuantityField('object-period',u.day)
    orbit = CharField('object-orbit',max_length=100)

class Geometry(Model):
    """
    PSG parameter model for fields starting with `GEOMETRY`.
    """
    geometry = CharField('geometry',max_length=20)
    ref = CharField('geometry-ref',max_length=50)
    offset = GeometryOffsetField()
    obs_altitude = CodedQuantityField(
        allowed_units=(u.AU,u.km,u_psg.diameter,u.pc),
        unit_codes=('AU','km','diameter','pc'),
        fmt='.4f',
        names=('geometry-obs-altitude','geometry-altitude-unit')
    )
    azimuth = QuantityField('geometry-azimuth',u.deg)
    user_parameter = GeometryUserParamField()
    stellar_type = CharChoicesField('geometry-stellar-type',('O','B','A','F','G','K','M',''),max_length=1)
    stellar_temperature = QuantityField('geometry-stellar-temperature',u.K)
    stellar_magnitude = FloatField('geometry-stellar-magnitude')
    # GEOMETRY-OBS-ANGLE -- Computed by PSG
    # GEOMETRY-SOLAR-ANGLE -- Computed by PSG
    disk_angles = IntegerField('geometry-disk-angles')
    # GEOMETRY-PLANET-FRACTION -- Computed by PSG
    # GEOMETRY-STAR-FRACTION -- Computed by PSG
    # GEOMETRY-STAR-DISTANCE -- Computed by PSG
    # GEOMETRY-ROTATION -- Computed by PSG
    # GEOMETRY-BRDFSCALER -- Computed by PSG

class Atmosphere(Model):
    structure = CharChoicesField('atmosphere-structure',('None','Equilibrium','Coma'))
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def _type_to_create(self, *args, **kwargs):
        cfg = kwargs.get('cfg')
        structure = self.structure.read(cfg)
        if structure == 'None':
            return NoAtmosphere
        elif structure == 'Equilibrium':
            return EquilibriumAtmosphere
        elif structure == 'Coma':
            return ComaAtmosphere
        else:
            raise ValueError(f'Unknown atmosphere type {structure}')
        
    
        
class NoAtmosphere(Atmosphere):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.structure.value = 'None'

class EquilibriumAtmosphere(Atmosphere):
    pressure = CodedQuantityField(
        # pylint: disable-next=no-member
        allowed_units=(u.Pa,u.bar,u_psg.kbar,u_psg.mbar,u_psg.ubar,cds.atm,u.torr,imperial.psi),
        unit_codes=('Pa','bar','kbar','mbar','ubar','atm','torr','psi'), # what is `at`?
        fmt = '.4e', names=('atmosphere-pressure','atmosphere-punit')
    )
    temperature = QuantityField('atmosphere-temperature',u.K)
    weight = QuantityField('atmosphere-weight',u.Unit('g mol-1'))
    continuum = CharField('atmosphere-continuum',max_length=300)
    molecules = MoleculesField()
    aerosols = AerosolsField()
    nmax = IntegerField('atmosphere-nmax')
    lmax = IntegerField('atmosphere-lmax')
    description = CharField('atmosphere-description',max_length=200)
    profile = ProfileField()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.structure.value = 'Equilibrium'

class ComaAtmosphere(Atmosphere):
    gas_production = QuantityField('atmosphere-pressure',u.Unit('s-1'))
    at_1au = BooleanField('atmosphere-punit',true='gasau',false='gas')
    expansion_velocity = QuantityField('atmosphere-weight',u.Unit('m s-1'))
    continuum = CharField('atmosphere-continuum',max_length=300)
    molecules = MoleculesField()
    aerosols = AerosolsField()
    nmax = IntegerField('atmosphere-nmax')
    lmax = IntegerField('atmosphere-lmax')
    tau = QuantityField('atmosphere-tau',u.s)
    description = CharField('atmosphere-description',max_length=200)
    profile = ProfileField()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.structure.value = 'Coma'
    
    

class Generator(Model):
    resolution_kernel = BooleanField('generator-resolutionkernel')
    gas_model = BooleanField('generator-gasmodel')
    continuum_model = BooleanField('generator-cont-model')
    continuum_stellar = BooleanField('generator-cont-stellar')
    apply_telluric_noise = BooleanField('generator-trans-show')
    apply_telluir_obs = BooleanField('generator-trans-apply')
    telluric_params = CharField('generator-trans',max_length=20)
    rad_units = CharChoicesField(
        'generator-radunits',
        options=tuple(key for key in u_psg.radiance_units.keys())
    )
    log_rad = BooleanField('generator-lograd')
    gcm_binning = IntegerField('generator-gcm-binning')
    
    
    
class Telescope(Model):
    """
    Base class for telescopes.
    """
    telescope = CharChoicesField(
        'generator-telescope',
        options = ('SINGLE','ARRAY','CORONA','AOTF','LIDAR')
    )
    apperture = QuantityField('generator-diamtele',u.Unit('m'))
    zodi = FloatField('generator-telescope2')
    fov = CodedQuantityField(
        allowed_units=(u.arcsec, u.arcmin, u.deg, u.km, u_psg.diameter, u_psg.diffraction),
        unit_codes=('arcsec','arcmin','deg','km','diameter','diffrac'),
        fmt = '.4e',
        names=('generator-beam','generator-beamunit')
    )
    range1 = CodedQuantityField(
        allowed_units=(u.um,u.nm, u.mm, u.AA, u.Unit('cm-1'),
                       u.MHz, u.GHz, u.kHz),
        unit_codes=('um','nm','mm','An','cm','MHz','GHz','kHz'),
        fmt = '.4e', names=('generator-range1','generator-rangeunit')
    )
    range2 = CodedQuantityField(
        allowed_units=(u.um,u.nm, u.mm, u.AA, u.Unit('cm-1'),
                       u.MHz, u.GHz, u.kHz),
        unit_codes=('um','nm','mm','An','cm','MHz','GHz','kHz'),
        fmt = '.4e', names=('generator-range2','generator-rangeunit')
    )
    resolution = CodedQuantityField(
        allowed_units=(u_psg.resolving_power,u.um,u.nm,u.mm,u.AA,
                       u.Unit('cm-1'),u.MHz,u.GHz,u.kHz),
        unit_codes=('RP','um','nm','mm','An','cm','MHz','GHz','kHz'),
        fmt = '.4e', names=('generator-resolution','generator-resolutionunit')
    )
    def _type_to_create(self, *args, **kwargs):
        cfg = kwargs['cfg']
        value = self.telescope.read(cfg)
        if value == 'SINGLE':
            return SingleTelescope
        elif value == 'ARRAY':
            return Interferometer
        elif value == 'CORONA':
            return Coronagraph
        elif value == 'AOTF':
            return AOTF
        elif value == 'LIDAR':
            return LIDAR
        else:
            raise ValueError(f'Unknown telescope type: {value}')
        

class Noise(Model):
    """
    Base class for noise models.
    """
    noise_type = CharChoicesField(
        'generator-noise',
        options=('NO','TRX','RMS','BKG','NEP','D*','CCD')
    )
    exp_time = QuantityField('generator-noisetime',u.s)
    n_frames = IntegerField('generator-noiseframes')
    n_pixels = IntegerField('generator-noisepixels')
    def _type_to_create(self, *args, **kwargs):
        cfg = kwargs['cfg']
        value = self.noise_type.read(cfg)
        if value == 'NO':
            return Noiseless
        elif value == 'TRX':
            return RecieverTemperatureNoise
        elif value == 'RMS':
            return ConstantNoise
        elif value == 'BKG':
            return ConstantNoiseWithBackground
        elif value == 'NEP':
            return PowerEquivalentNoise
        elif value == 'D*':
            return Detectability
        elif value == 'CCD':
            return CCD
        else:
            raise ValueError(f'Unknown noise type: {value}')


class SingleTelescope(Telescope):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.telescope.value = 'SINGLE'

class Interferometer(Telescope):
    n_telescopes = IntegerField('generator-telescope1')
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.telescope.value = 'ARRAY'

class Coronagraph(Telescope):
    contrast = FloatField('generator-telescope1')
    iwa = FloatField('generator-telescope3')
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.telescope.value = 'CORONA'

class AOTF(Telescope):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.telescope.value = 'AOTF'
class LIDAR(Telescope):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.telescope.value = 'LIDAR'

class Noiseless(Noise):
    thoughput = FloatField('generator-noiseoeff')
    emissivity = FloatField('generator-noieoemis')
    temperature = QuantityField('generator-noisetemp',u.K)
    desc = CharField('generator-instrument',max_length=500)
    pixel_depth = QuantityField('generator-noisewell',u.electron)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.noise_type.value = 'NO'

class RecieverTemperatureNoise(Noise):
    temperature = FloatField('generator-noise1')
    g_factor = FloatField('generator-noise2')
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.noise_type.value = 'TRX'

class ConstantNoise(Noise):
    sigma = FloatField('generator-noise1')
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.noise_type.value = 'RMS'

class ConstantNoiseWithBackground(Noise):
    sigma = FloatField('generator-noise1')
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.noise_type.value = 'BKG'

class PowerEquivalentNoise(Noise):
    sensitivity = QuantityField('generator-noise1',u.W/u.Hz**(1/2))
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.noise_type.value = 'NEP'

class Detectability(Noise):
    sensitivity = QuantityField('generator-noise1',u.cm*u.Hz**(1/2)/u.W)
    pixel_size = QuantityField('generator-noise2',u.um)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.noise_type.value = 'D*'

class CCD(Noise):
    read_noise = QuantityField('generator-noise1',u.electron)
    dark_current = QuantityField('generator-noise2',u.electron/u.s)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.noise_type.value = 'CCD'
