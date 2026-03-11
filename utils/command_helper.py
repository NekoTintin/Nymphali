from cmds.danbooru import cmd_danbooru
import cmds.jellyfin as jellyfin
from cmds.tools import cmd_ping, cmd_help, cmd_short_url
from cmds.kemono import random_from_creator

COMMANDS_LIST = {
	"help": {
		"ptr": cmd_help,
		"desc": "Affiche la liste des commandes disponibles.",
		"usage": "?help",
		"reactions": False
	},
	"ping": {
		"ptr": cmd_ping,
		"desc": "Répond avec 'Pong !' pour vérifier que le bot est en ligne.",
		"usage": "?ping",
		"reactions": False
	},
	"danbooru": {
		"ptr": cmd_danbooru,
		"desc": "Recherche une image sur Danbooru.",
		"usage": "?danbooru nsfw[yes/no] tags[...]",
		"reactions": False
	},
	"kemono": {
		"ptr": random_from_creator,
		"desc": "Recherche un post aléatoire d'un créateur sur Kemono.",
		"usage": "?kemono [service] [créateur]",
		"reactions": False
	},
	"jfs": {
		"ptr": jellyfin.cmd_jellyfin_search,
		"desc": "Recherche un média sur Jellyfin.",
		"usage": "?jfs [recherche]",
		"reactions": True
	},
	"short": {
		"ptr": cmd_short_url,
		"desc": "Renvoie une URL courte.",
		"usage": "?short [URL]",
		"reactions": False
	},
}