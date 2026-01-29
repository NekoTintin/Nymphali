import httpx
import utils

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