from nio import MatrixRoom, RoomMessageText, UploadResponse
import httpx
from danbooru import search_on_danbooru
import mimetypes
import io
from PIL import Image

import utils
import cmds.jellyfin


COMMANDS_HELP = {
    "help": "Affiche cette aide avec la liste des commandes disponibles.",
	"ping": "Répond avec 'Pong !' pour vérifier que le bot est en ligne.",
	"jfs": "Recherche un média sur Jellyfin. Usage : !jfs [query]"
}

async def cmd_help(bot, room: MatrixRoom, event: RoomMessageText, args: list):
	plain_text = "Commandes disponibles :\n"
	html_text = "<h4>Commandes disponibles :</h4><ul>"

	for cmd, desc in COMMANDS_HELP.items():
		plain_text += f"- {bot.prefix}{cmd}: {desc}\n"
		html_text += f"<li><strong>{bot.prefix}{cmd}</strong> : {desc}</li>"
    
	html_text += "</ul>"

	await bot.client.room_send(
		room_id=room.room_id,
		message_type="m.room.message",
		content={
			"msgtype": "m.text",
			"body": plain_text,
			"format": "org.matrix.custom.html",
			"formatted_body": html_text}
	)

async def cmd_ping(bot, room: MatrixRoom, event: RoomMessageText, args: list):
	await bot.client.room_send(
		room_id=room.room_id,
		message_type="m.room.message",
		content={"msgtype": "m.text", "body": "Pong !"}
	)

async def cmd_danbooru(bot, room: MatrixRoom, event: RoomMessageText, args: list):
	if not args:
		await utils.send_msg(bot, room, "Usage : !danbooru nsfw[yes/no] tags[...]")
		return

	if args[0].lower() not in ["yes", "no"]:
		return
	nsfw = args[0].lower() == "yes"
	tags = args[1:]
 
	data = await search_on_danbooru(bot, room, tags, nsfw)
	if not data or not "file_url" in data:
		return

	async with httpx.AsyncClient() as client:
		try:
			rep = await client.get(data["file_url"])
			if rep.status_code != 200:
				await utils.send_msg(bot, room, "Erreur lors du téléchargement de l'image.")
				return

			image_bytes = rep.content

			with Image.open(io.BytesIO(image_bytes)) as img:
				width, height = img.size

			mime_type = rep.headers.get("Content-Type", "image/png")
			ext = mimetypes.guess_extension(mime_type) or ".jpg"
			filename = f"danbooru_{data.get('id', 'image')}{ext}"

			image_stream = io.BytesIO(image_bytes)

			resp, maybe_key = await bot.client.upload(
				image_stream,
				content_type=mime_type,
				filename=filename,
				filesize=len(image_bytes)
			)

			if isinstance(resp, UploadResponse):
				await bot.client.room_send(
					room.room_id,
					"m.room.message",
					{	"msgtype": "m.image",
						"body": filename,
						"url": resp.content_uri,
						"info": {
							"mimetype": mime_type,
							"size": len(image_bytes),
							"w": width,
							"h": height
			}})
		except Exception as e:
			await utils.send_msg(bot, room, f"Erreur lors du traitement de l'image : {e}")

COMMANDS_LIST = {
	"help": cmd_help,
	"ping": cmd_ping,
	"danbooru": cmd_danbooru,
	"jfs": cmds.jellyfin.cmd_jellyfin_search
}

