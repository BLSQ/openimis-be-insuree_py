from graphql.error import GraphQLError


def camel_to_snake(camelString):
    snake = []
    for i, char in enumerate(camelString):
        if char.isupper():
            if i != 0:
                snake.append("_")
            snake.append(char.lower())
        else:
            snake.append(char)
    return "".join(snake)


def hera_life_event_handler(nin, context):
    from insuree.adapters import HeraAdapter, WebhookEventManager

    try:
        if response := HeraAdapter(nin=nin, operation="get_one_person_info").get_data():
            crud = {
                "CREATE": "create_or_update_insuree",
                "UPDATE": "create_or_update_insuree",
                # "DELETE": 'delete_insuree',
            }
            for key, method in crud.items():
                if key in context:
                    insuree_manager_method = getattr(WebhookEventManager(), method)
                    snake_case_data = {
                        camel_to_snake(key): value for key, value in response.items()
                    }
                    insuree_manager_method(nin=nin, **snake_case_data)
                    break
    except Exception as exc:
        # Schedule a retry of the task in 10 seconds
        raise GraphQLError(exc) from exc
