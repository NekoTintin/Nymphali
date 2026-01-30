from cmds.danbooru import cmd_danbooru
import cmds.jellyfin as jellyfin
from cmds.tools import cmd_ping, cmd_help

COMMANDS_LIST = {
	"help": {
		"ptr": cmd_help,
		"desc": "Affiche la liste des commandes disponibles.",
		"usage": "?help"
	},
	"ping": {
		"ptr": cmd_ping,
		"desc": "Répond avec 'Pong !' pour vérifier que le bot est en ligne.",
		"usage": "?ping"
	},
	"danbooru": {
		"ptr": cmd_danbooru,
		"desc": "Recherche une image sur Danbooru.",
		"usage": "?danbooru nsfw[yes/no] tags[...]"
	},
	"jfs": {
		"ptr": jellyfin.cmd_jellyfin_search,
		"desc": "Recherche un média sur Jellyfin.",
		"usage": "?jfs [recherche]"
	}
}