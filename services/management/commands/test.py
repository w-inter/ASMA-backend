# !/usr/bin/env python3
from django.core.management.base import BaseCommand, CommandError
from services.classes.classes import PositionGPS
from util.coordinates_matching import matching_coordinates
from services.models import Geoname
from services.classes.classes import EntityGeoNames
from services.algorithms.algorithm_align import match_type_correspondence, match_type_synonyms
from services.algorithms.algorithm_blocking import blocking_function
from decimal import *
from util.util import print_tags
__author__ = 'Amaia Nazabal'


class Command(BaseCommand):
    help = 'This service allows import all the correspondences between types with a criteria related to the quantity' \
           ' of people how made the correspondences.'

    def handle(self, *args, **options):

        try:

            # position_gn = PositionGPS(Decimal(42.5116200), Decimal(1.5340800))
            # position_osm = PositionGPS(Decimal(42.5114983), Decimal(1.5344814))
            #
            # coordinates_matching = matching_coordinates(position_gn, position_osm)
            # print(coordinates_matching)

            gn_entity = Geoname.objects.get(pk=8224606)
            geoname = EntityGeoNames(id=gn_entity.id, name=gn_entity.name, latitude=gn_entity.latitude,
                                    longitude=gn_entity.longitude, feature_class=gn_entity.fclass,
                                    feature_code=gn_entity.fcode)
            list_block_entities = blocking_function(geoname)
            for entity_osm in list_block_entities:
                print("------------------------------------------------------------")
                tag_osm = type_tag_osm, matching_type_level = match_type_correspondence(geoname, entity_osm.get('tag_list'))
                if not matching_type_level:
                    tag_osm, _ = type_tag_osm, matching_type_level = match_type_synonyms(geoname, entity_osm.get('tag_list'))

                print(geoname.get_feature_class(), geoname.get_feature_code())
                print("TAG::::", tag_osm.key, tag_osm.value)
                print("matching_type_level", matching_type_level)
                print(entity_osm['entity_osm'].id)
                print("------------------------------------------------------------")

        except Exception as error:
            raise CommandError(error)
