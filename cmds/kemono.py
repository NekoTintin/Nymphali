from nio import MatrixRoom, RoomMessageText, UploadResponse
import httpx
import mimetypes
import io
from PIL import Image
from random import choice

import utils.utils as utils

service_list = {
	"patreon",
	"fanbox",
	"fantia",
	"gumroad"
}

async def kemono_request(url: str):
	headers = {
		"Accept": "text/css"
	}

	async with httpx.AsyncClient() as client:
		resp = await client.get(url, headers=headers)
		if resp.status_code == 200:
			return resp.json()
		else:
			return None

async def random_from_creator(bot, room: MatrixRoom, event: RoomMessageText, args: list):
	await bot.client.room_redact(room.room_id, event.event_id, reason="Nettoyage du message de commande")
	if args == None or len(args) != 2:
		await utils.send_msg(bot, room, "Usage : ?kemono [service] [creator_id]")
		return
	
	if args[0] not in service_list:
		await utils.send_msg(bot, room, f"Service inconnu. Services disponibles : {', '.join(service_list)}")
		return

	post_list = await kemono_request(f"https://kemono.cr/api/v1/{args[0]}/user/{args[1]}/posts")
	if post_list == None or len(post_list) == 0:
		await utils.send_msg(bot, room, "Aucun post trouvé pour ce créateur.")
		return
	
	# Boucler jusqu'à trouver un post avec des images
	post = None
	for _ in range(min(10, len(post_list))):  # Essayer max 10 posts
		candidate = choice(post_list)
		if candidate.get("attachments") and len(candidate["attachments"]) > 0:
			post = candidate
			break
	
	if post is None:
		await utils.send_msg(bot, room, "Aucun post avec images trouvé pour ce créateur.")
		return
	
	print(f"URL: https://kemono.cr/{args[0]}/user/{args[1]}/post/{post['id']}")

	images_data = post["attachments"][:4]
	# Filtrer pour garder que les images
	images_data = [img for img in images_data if img['path'].lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))]
	
	if not images_data:
		await utils.send_msg(bot, room, "Aucune image trouvée dans les attachments.")
		return
	
	images = []
	
	async with httpx.AsyncClient() as client:
		for img_info in images_data:
			url = f"https://n1.kemono.cr/data{img_info['path']}"
			resp = await client.get(url, follow_redirects=True)
			print(f"DEBUG: {url} - Status: {resp.status_code}")
			if resp.status_code == 200:
				images.append(Image.open(io.BytesIO(resp.content)))
			else:
				await utils.send_msg(bot, room, f"Erreur lors du téléchargement d'une image (status {resp.status_code}).")
				return

	num_images = len(images)
	if num_images == 1:
		grid_cols, grid_rows = 1, 1
	elif num_images == 2:
		grid_cols, grid_rows = 2, 1
	elif num_images == 3:
		grid_cols, grid_rows = 2, 2
	else:
		grid_cols, grid_rows = 2, 2

	# Redimensionner les images pour éviter qu'elles soient trop grosses
	max_size = (350, 350)
	for img in images:
		img.thumbnail(max_size, Image.Resampling.LANCZOS)

	img_width, img_height = images[0].size

	grid_width = grid_cols * img_width
	grid_height = grid_rows * img_height
	grid = Image.new("RGB", (grid_width, grid_height))

	for idx, img in enumerate(images):
		x = (idx % grid_cols) * img_width
		y = (idx // grid_cols) * img_height
		grid.paste(img, (x, y))

	buffer = io.BytesIO()
	grid.save(buffer, format="WEBP", quality=40)
	buffer.seek(0)
	image_bytes = buffer.getvalue()

	mime_type = "image/webp"
	ext = ".webp"
	filename = f"kemono_{args[0]}_{args[1]}{ext}"

	try:
		# Envoyer le titre en message texte
		#await utils.send_msg(bot, room, post.get("title", "Post sans titre"))

		# Uploader l'image
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
				{
					"msgtype": "m.image",
					"body": filename,
					"url": resp.content_uri,
					"info": {
						"mimetype": mime_type,
						"size": len(image_bytes),
						"w": grid_width,
						"h": grid_height
					}
				}
			)
		else:
			await utils.send_msg(bot, room, "Erreur lors de l'upload de l'image.")
	except Exception as e:
		await utils.send_msg(bot, room, f"Erreur lors du traitement : {str(e)}")