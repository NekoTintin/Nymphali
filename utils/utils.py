from nio import MatrixRoom

async def send_msg(bot, room: MatrixRoom, message: str):
	await bot.client.room_send(
		room_id=room.room_id,
		message_type="m.room.message",
		content={"msgtype": "m.text", "body": message}
	)
 
def print_with_color(message: str, color_code: str):
	print(f"{color_code}{message}\033[0m")