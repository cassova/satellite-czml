# satellite_czml
# Author: Nicholas Miller (miller.nicholas.a@gmail.com)
# https://github.com/cassova/satellite-czml


from .czml import (CZML, Billboard, CZMLPacket, Description, Label,
                   Path, Position)
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv

from datetime import datetime, timedelta
import pytz
import random
import math

class satellite():
    '''
    Creates an instance of a satellite to be included in the CZML document
    based on a TLE
    '''
    name = ''
    description = ''
    color = ''
    image = ("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNS" +
             "R0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAADJSURBVDhPnZ" +
             "HRDcMgEEMZjVEYpaNklIzSEfLfD4qNnXAJSFWfhO7w2Zc0Tf9QG2rXrEzSUeZLOGm47WoH95x3" +
             "Hl3jEgilvDgsOQUTqsNl68ezEwn1vae6lceSEEYvvWNT/Rxc4CXQNGadho1NXoJ+9iaqc2xi2x" +
             "bt23PJCDIB6TQjOC6Bho/sDy3fBQT8PrVhibU7yBFcEPaRxOoeTwbwByCOYf9VGp1BYI1BA+Ee" +
             "HhmfzKbBoJEQwn1yzUZtyspIQUha85MpkNIXB7GizqDEECsAAAAASUVORK5CYII=")
    marker_scale = 1.5
    start_time = datetime.utcnow().replace(tzinfo=pytz.UTC)
    end_time = start_time + timedelta(hours=24)
    tle = []
    tle_obj = None
    
    czmlMarker = None
    czmlLabel = None
    czmlPath = None
    czmlPosition = None
    
    def __init__(self, tle, name=None, description=None, color=None, image=None,
                 marker_scale=None, use_default_image=True, start_time=None, end_time=None):

        # Validate the inputs
        if name is None:
            self.tle = self.__check_tle_for_names(tle)
            self.name = tle[0]
        else:
            self.tle = self.__check_tle(tle)
            self.name = name

        if len(tle) == 3:
            self.tle = tle[1:]
        else:
            self.tle = tle

        if description is not None:
            self.description = description
        else:
            self.description = 'Orbit of Satellite: ' + self.name

        self.color = self.__check_color(color)

        if image is not None:
            self.image = image
        elif not use_default_image:
            # TODO: Do something here to ensure we display a colored dot instead
            self.image = None

        self.marker_scale = marker_scale or self.marker_scale

        if start_time is not None:
            self.start_time = start_time
        if end_time is not None:
            self.end_time = end_time

        self.tle_obj = twoline2rv(self.tle[0], self.tle[1], wgs72)

    def __check_tle_for_names(self, tle):
        '''
        Checks if TLE has a name by seeing if 3 records exist
        (name, TLE1, TLE2) when name_list is None
        '''
        if len(tle) != 3:
            raise Exception(f"Satellite TLE only has {len(tle)} elements.  Expected 3 " +
                            f"or pass in a name.\nTLE:\n{tle}")
        return tle[1:]

    def __check_tle(self, tle):
        '''
        Checks if TLE has either 2 or 3 records 
        [name (optional), TLE1, TLE2]
        '''
        if len(tle) not in [2,3]:
            raise Exception(f"Satellite TLE only has {len(tle)} elements.  Expected 2 or 3." +
                            f"(first line containing name is optional\nTLE:\n{tle}")
        return tle

    def __check_color(self, color):
        '''
        Checks if color is valid or generates a random one
        '''
        if color is not None and len(color) not in [3,4]:
            raise Exception(f"Color for {self.__name} only has {len(color)} elements.  Expected 3 or 4." +
                             "(last one, alpha, being optional)")
        elif color is not None:
            for x in color:
                if x is None or x < 0 or x > 255:
                    raise Exception(f"Color value {x} is not supported. Expected value between 0 and 255.")
        else:
            color = [random.randrange(256) for x in range(3)]

        if len(color) == 3:
            # Default missing alpha to 255
            color.append(255)

        return color

    def build_marker(self, image=None, marker_scale=None, show_marker=True):
        '''
        Creates the satellite marker (i.e. billboard)
        '''
        if self.czmlMarker is None:
            self.czmlMarker = Billboard(scale=marker_scale or self.marker_scale,
                                        show=show_marker)
            self.czmlMarker.image = image or self.image
        return self.czmlMarker

    def build_label(self, color=None,
                    font='11pt Lucida Console',
                    hOrigin='LEFT',
                    vOrigin='CENTER',
                    outlineColor=[0, 0, 0, 255],
                    outlineWidth=2,
                    pixelOffset={"cartesian2": [12, 0]},
                    style='FILL_AND_OUTLINE',
                    show=True):
        '''
        Creates the satellite label
        '''
        if self.czmlLabel is None:
            self.czmlLabel = Label(text=self.name, show=show)
            self.czmlLabel.fillColor = {"rgba": color or self.color}
            self.czmlLabel.font = font
            self.czmlLabel.horizontalOrigin = hOrigin
            self.czmlLabel.verticalOrigin = vOrigin
            self.czmlLabel.outlineColor = {"rgba": outlineColor}
            self.czmlLabel.outlineWidth = outlineWidth
            self.czmlLabel.pixelOffset = pixelOffset
            self.czmlLabel.style = style
        return self.czmlLabel

    def build_path(self, show=True,
                   interval=None,
                   width=1,
                   materialColor=None,
                   resolution=120,
                   lead_times=None,
                   trail_times=None,
                   start_time=None,
                   end_time=None):
        '''
        Creates the satellite path
        '''
        if self.czmlPath is None:
            if interval is None:
                interval = self.start_time.isoformat() + "/" + self.end_time.isoformat()

            self.czmlPath = Path()
            self.czmlPath.show=[{"interval": interval, "boolean": show}]
            self.czmlPath.width = width
            self.czmlPath.material = {"solidColor": {"color": {"rgba": materialColor or self.color}}}
            self.czmlPath.resolution = resolution

            if lead_times is None and trail_times is None:
                lead_times, trail_times = self.build_lead_trail_times(start_time, end_time)
            self.czmlPath.leadTime = lead_times
            self.czmlPath.trailTime = trail_times

        return self.czmlPath

    def build_position(self,
                       start_time=None,
                       end_time=None,
                       interpolationAlgorithm = "LAGRANGE",
                       interpolationDegree = 5,
                       referenceFrame = "INERTIAL",
                       tle_object=None,
                       step=300):
        '''
        Creates the satellite positions and settings
        '''
        start_time = start_time or self.start_time
        end_time = end_time or self.end_time
        tle_object = tle_object or self.tle_obj

        if self.czmlPosition is None:
            self.czmlPosition = Position()
            self.czmlPosition.interpolationAlgorithm = interpolationAlgorithm
            self.czmlPosition.interpolationDegree = interpolationDegree
            self.czmlPosition.referenceFrame = referenceFrame
            self.czmlPosition.epoch = start_time.isoformat()

            number_of_positions = int((end_time - start_time).total_seconds()/300)
            number_of_positions += 5 # so there is more than 1
            time_step=0

            positions=[]
            for _ in range(number_of_positions):
                current_time = start_time + timedelta(seconds=time_step)
                eci_position, _ = tle_object.propagate(current_time.year, current_time.month,
                                                       current_time.day, current_time.hour,
                                                       current_time.minute, current_time.second)

                positions.append(time_step)
                positions.append(eci_position[0] * 1000)  # converts km's to m's
                positions.append(eci_position[1] * 1000)
                positions.append(eci_position[2] * 1000)
                time_step += step
            self.czmlPosition.cartesian = positions
        return self.czmlPosition

    def get_orbital_time(self):
        '''
        Extracts the number of orbits per day from the tle and calcualtes the
        time per orbit in minutes
        '''
        return (24.0/float(self.tle[1][52:63]))*60.0

    def build_lead_trail_times(self, start_time=None, end_time=None):
        '''
        Builds the lead and trail time for the orbit path
        '''
        start_time = start_time or self.start_time
        end_time = end_time or self.end_time

        minutes_in_sim = int((end_time - start_time).total_seconds()/60)
        left_over_minutes = minutes_in_sim % self.get_orbital_time()
        number_of_full_orbits = math.floor(minutes_in_sim / self.get_orbital_time())
        sp_start = start_time
        sp_end = sp_start + timedelta(minutes=left_over_minutes)
        sp_interval = (sp_start.isoformat() + '/' + sp_end.isoformat())
        orbital_time_in_seconds = (self.get_orbital_time() * 60.0)

        lead_times=[]
        trail_times=[]
        for _ in range(number_of_full_orbits + 1):
            lead_times.append({
                "interval": sp_interval,
                "epoch": sp_start.isoformat(),
                "number": [
                    0, orbital_time_in_seconds,
                    orbital_time_in_seconds, 0
                ]
            })
            trail_times.append({
                "interval": sp_interval,
                "epoch": sp_start.isoformat(),
                "number": [
                    0, 0,
                    orbital_time_in_seconds, orbital_time_in_seconds
                ]
            })

            sp_start = sp_end
            sp_end = (sp_start + timedelta(minutes=self.get_orbital_time()))
            sp_interval = (sp_start.isoformat() + '/' + sp_end.isoformat())
        return lead_times, trail_times

    def build_lead_time(self, start_time=None, end_time=None):
        '''
        Builds the lead time for the orbit path
        '''
        start_time = start_time or self.start_time
        end_time = end_time or self.end_time

        minutes_in_sim = int((end_time - start_time).total_seconds()/60)
        left_over_minutes = minutes_in_sim % self.get_orbital_time()
        number_of_full_orbits = math.floor(minutes_in_sim / self.get_orbital_time())
        sp_start = start_time
        sp_end = sp_start + timedelta(minutes=left_over_minutes)
        sp_interval = (sp_start.isoformat() + '/' + sp_end.isoformat())
        orbital_time_in_seconds = (self.get_orbital_time() * 60.0)

        lead_times=[]
        for _ in range(number_of_full_orbits + 1):
            lead_times.append({
                "interval": sp_interval,
                "epoch": sp_start.isoformat(),
                "number": [
                    0, orbital_time_in_seconds,
                    orbital_time_in_seconds, 0
                ]
            })

            sp_start = sp_end
            sp_end = (sp_start + timedelta(minutes=self.get_orbital_time()))
            sp_interval = (sp_start.isoformat() + '/' + sp_end.isoformat())
        return lead_times

    def build_trail_time(self, start_time=None, end_time=None):
        '''
        Builds the trail time for the orbit path
        '''
        start_time = start_time or self.start_time
        end_time = end_time or self.end_time

        minutes_in_sim = int((end_time - start_time).total_seconds()/60)
        left_over_minutes = minutes_in_sim % self.get_orbital_time()
        number_of_full_orbits = math.floor(minutes_in_sim / self.get_orbital_time())
        sp_start = start_time
        sp_end = sp_start + timedelta(minutes=left_over_minutes)
        sp_interval = (sp_start.isoformat() + '/' + sp_end.isoformat())
        orbital_time_in_seconds = (self.get_orbital_time() * 60.0)

        trail_times=[]
        for _ in range(number_of_full_orbits + 1):
            trail_times.append({
                "interval": sp_interval,
                "epoch": sp_start.isoformat(),
                "number": [
                    0, 0,
                    orbital_time_in_seconds, orbital_time_in_seconds
                ]
            })

            sp_start = sp_end
            sp_end = (sp_start + timedelta(minutes=self.get_orbital_time()))
            sp_interval = (sp_start.isoformat() + '/' + sp_end.isoformat())
        return trail_times

class satellite_czml():
    '''
    Generates the CZML document used by Cesium for plotting Satellites
    using TLE entries
    '''

    start_time = datetime.utcnow().replace(tzinfo=pytz.UTC)
    end_time = start_time + timedelta(hours=24)
    speed_multiplier = 60
    default_seed = 0

    satellites = {}

    def __init__(self):
        '''
        Initialize an empty object
        '''
        return True

    def __init__(self, tle_list, start_time=None, end_time=None, name_list=None,
                 description_list=None, color_list=None, image_list=None,
                 use_default_image=True, marker_scale_list=None, speed_multiplier=None,
                 use_utc=True, seed=None):
        '''
        Initialize a filled object
        '''

        # Validate the inputs and default to list of None's if None
        ex_len = len(tle_list)
        name_list        = self.__check_list(ex_len, name_list, 'name_list')
        description_list = self.__check_list(ex_len, description_list, 'description_list')
        color_list       = self.__check_list(ex_len, color_list, 'color_list')
        image_list       = self.__check_list(ex_len, image_list, 'image_list')
        marker_scale_list = self.__check_list(ex_len, marker_scale_list, 'marker_scale_list')

        if start_time != None or end_time != None:
            self.set_start_end_time(start_time or self.start_time,
                                    end_time or self.end_time)

        # Set the seed now before we generate colors
        self.set_seed(seed)

        # Set speed multiplier
        self.set_speed_multiplier(speed_multiplier)

        # Create Satellite for each TLE in list
        for i,tle in enumerate(tle_list):
            sat = satellite(tle=tle,
                            name=name_list[i],
                            description=description_list[i],
                            color=color_list[i],
                            image=image_list[i],
                            marker_scale=marker_scale_list[i],
                            use_default_image=use_default_image,
                            start_time=self.start_time,
                            end_time=self.end_time)
            
            self.add_satellite(sat)

    def __check_list(self, tle_len, lst, lst_name=None):
        '''
        Checks that the list contains the same number of elements
        as the number of TLEs. If None, default to a list of Nones.
        '''
        if lst != None and len(lst) != tle_len:
            if lst_name != None:
                lst_name = 'list'
            raise Exception(f"Number of elements in {lst_name} is {len(lst)} " +
                            f"and doesn't match number of TLEs: {tle_len}")
            return False
        return lst or [None for x in range(tle_len)]

    def add_satellite(self, sat):
        '''
        Adds (or updates) instance of Satellite
        '''
        self.satellites[sat.name] = sat
        return True

    def get_satellite(self, name):
        '''
        Returns instance of Satellite
        '''
        return self.satellites[name]

    def remove_satellite(self, name):
        '''
        Removes instance of Satellite
        '''
        del self.satellites[name]
        return True

    def set_start_end_time(self, start_time, end_time, set_utc=True):
        '''
        Sets the start and end time
        '''
        if set_utc == True:
            start_time = start_time.replace(tzinfo=pytz.UTC)
            end_time = end_time.replace(tzinfo=pytz.UTC)
        self.start_time = start_time
        self.end_time = end_time

        return True

    def set_speed_multiplier(self, speed):
        '''
        Sets the speed multiplier (how fast the satellites move)
        '''
        self.speed_multiplier = speed or self.speed_multiplier
        return True

    def set_seed(self, seed):
        '''
        Set the random seed. Only effects satellites not yet added.
        '''
        random.seed(seed or self.default_seed)
        return True

    def get_czml(self):
        '''
        Returns a CZML string
        '''

        # Initialize the CZML document
        interval = self.start_time.isoformat() + "/" + self.end_time.isoformat()
        doc = CZML()
        packet = CZMLPacket(id='document', version='1.0')
        packet.clock = {"interval": interval,
                        "currentTime": self.start_time.isoformat(),
                        "multiplier": self.speed_multiplier,
                        "range": "LOOP_STOP",
                        "step": "SYSTEM_CLOCK_MULTIPLIER"}
        doc.packets.append(packet)

        # Add each satellite
        for name, sat in self.satellites.items():
            # Initialize satellite CZML data
            sat_packet = CZMLPacket(id=name)
            sat_packet.availability = interval
            sat_packet.description = Description(sat.description)

            sat_packet.billboard = sat.build_marker()
            sat_packet.label = sat.build_label()
            sat_packet.path = sat.build_path()
            sat_packet.position = sat.build_position()

            doc.packets.append(sat_packet)

        return str(doc)
