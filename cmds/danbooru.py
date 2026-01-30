from nio import MatrixRoom, RoomMessageText, UploadResponse
import httpx
import mimetypes
import io
from PIL import Image

import utils.utils as utils

async def create_request(tags: str, nsfw: bool) -> dict:
	url = "https://danbooru.donmai.us/posts/random.json"
	params = { "tags": tags }
	headers = { "Accept": "application/json" }

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
		if not rep or "file_url" not in rep:
			await utils.send_msg(bot, room, "Aucun résultat trouvé pour les tags fournis.")
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