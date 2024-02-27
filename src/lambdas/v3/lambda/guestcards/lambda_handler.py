from controller import guest_card_controller


def lambda_handler(event, context):
    response = guest_card_controller.GuestCardController()
    pass

