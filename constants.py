# =============================================================================
#          File: constants.py
#        Author: Andre Brener
#       Created: 22 Aug 2017
# Last Modified: 21 Nov 2018
#   Description: Shared configuration constants (competitions, dates) and the
#                team abbreviation -> display name map used by the graphs.
# =============================================================================
from datetime import date

COMPETITION_DICT = {
    'primera_division': 'arg.1',
    'copa_argentina': 'arg.copa',
    'copa_libertadores': 'conmebol.libertadores',
    'copa_sudamericana': 'conmebol.sudamericana',
    'recopa_sudamericana': 'conmebol.recopa',
    'world_cup': 'fifa.world',
    'confederations_cup': 'fifa.confederations',
    'europa_league': 'uefa.europa',
    'champions_league': 'uefa.champions',
}

COMPETITION = 'primera_division'

START_DATE = date(2017, 8, 27)
END_DATE = date(2017, 8, 28)

# Map of ESPN team abbreviations to display names. Shared by the graphing
# scripts (penalty_ratio.py, season_analysis.py) to avoid duplication.
TEAM_DICT = {
    'CABJ': 'Boca',
    'CARP': 'River',
    'SL': 'San Lorenzo',
    'ALDO': 'Aldosivi',
    'ARS': 'Arsenal',
    'BAN': 'Banfield',
    'BEL': 'Belgrano',
    'CAP': 'Patronato',
    'COL': 'Colón',
    'DYJ': 'Defensa y Justicia',
    'EST': 'Estudiantes',
    'GCM': 'Godoy Cruz',
    'GLP': 'GELP',
    'HUR': 'Huracán',
    'IND': 'Independiente',
    'LAN': 'Lanús',
    'NOB': 'Newells',
    'OBB': 'Olimpo',
    'QUI': 'Quilmes',
    'RAC': 'Racing',
    'RAF': 'A. Rafaela',
    'ROS': 'R. Central',
    'SARM': 'Sarmiento',
    'SMSJ': 'San Martin SJ',
    'TDC': 'Talleres',
    'TEMP': 'Temperley',
    'TIG': 'Tigre',
    'TUC': 'A. Tucuman',
    'USF': 'Unión',
    'VEL': 'Velez',
    'ARGJ': 'Argentinos Jrs',
    'CHA': 'Chacarita',
}
