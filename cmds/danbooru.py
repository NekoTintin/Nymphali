from nio import MatrixRoom, RoomMessageText, UploadResponse
import httpx
import mimetypes
import io
from PIL import Image

import utils.utils as utils

async def dan_msg(bot, room, data: dict, nsfw):
	artist = data.get("tag_string_artist", "inconnu")
	post_id = data.get("id", "")
	source_link = data.get("source", None)

	danbooru_link = f"https://danbooru.donmai.us/posts/{post_id}"

	body = f"Post de {artist} - Lien - Source"

	formatted_body = f"Post de {artist} - <a href='{danbooru_link}'>Lien</a>"
	if source_link:
		formatted_body += f" - <a href='{source_link}'>Source</a>"

	await bot.client.room_send(
		room.room_id,
		"m.room.message",
		{
			"msgtype": "m.text",
			"body": body,
			"format": "org.matrix.custom.html",
			"formatted_body": formatted_body
		}
	)


async def create_request(tags: str, nsfw: bool) -> dict:
	url = "https://danbooru.donmai.us/posts/random.json"
	params = { "tags": tags }
	headers = { 
		"Accept": "application/json",
		"User-Agent": "NymphaliBot/1.0 (Matrix Bot)"
	}

	async with httpx.AsyncClient() as client:
		resp = await client.get(url, params=params, headers=headers)
		if resp.status_code == 200:
			return resp.json()
		else:
			return None

async def search_on_danbooru(bot, room, tags: list, nsfw: bool=True) -> dict:
	search_tags = " ".join(tags)
	if (len(tags) < 1 or len(tags) > 3):
		await utils.send_msg(bot, room, "Veuillez fournir entre 1 et 3 tags pour la recherche.")
		return

	if nsfw:
		search_tags += " rating:e,q"
	else:
		search_tags += " rating:s,g"
	try:
		rep = await create_request(search_tags, nsfw)
		if not rep:
			await utils.send_msg(bot, room, "Aucun résultat trouvé pour les tags fournis.")
			return None
		if "file_url" not in rep:
			await utils.send_msg(bot, room, "Résultat trouvé mais pas d'URL de fichier.")
			return None
		return rep
	except Exception as e:
		await utils.send_msg(bot, room, f"Erreur lors de la requête à Danbooru : {e}")
		return None

# Bot command
async def cmd_danbooru(bot, room: MatrixRoom, event: RoomMessageText, args: list):
	if not args:
		await utils.send_msg(bot, room, "Usage : !danbooru nsfw[yes/no] tags[...]")
		return
	if len(args) < 2 or len(args) > 4:
		await utils.send_msg(bot, room, f"Erreur: Danbooru demande au moins 1 tag et au max 2 tags.")
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
			headers = {"User-Agent": "NymphaliBot/1.0 (Matrix Bot)"}
			rep = await client.get(data["file_url"], headers=headers)
			if rep.status_code != 200:
				await utils.send_msg(bot, room, f"Erreur lors du téléchargement de l'image (code {rep.status_code}).")
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

			await dan_msg(bot, room, data, nsfw)
			if isinstance(resp, UploadResponse):
				content = {
					"msgtype": "m.image",
					"body": filename,
					"url": resp.content_uri,
					"info": {
					    "mimetype": mime_type,
					    "size": len(image_bytes),
					    "w": width,
					    "h": height
					}
				}

				if nsfw:
					content["body"] = f"[SPOILER NSFW] {filename}"
					content["format"] = "org.matrix.custom.html"
					content["formatted_body"] = f'<span data-mx-spoiler="Contenu NSFW">Image : {filename}</span>'

				await bot.client.room_send(
					room.room_id,
					"m.room.message",
					content
				)
		except Exception as e:
			await utils.send_msg(bot, room, f"Erreur lors du traitement de l'image : {e}")