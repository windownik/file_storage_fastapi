get_me_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {
                            "ok": True,
                            "user": {
                                "user_id": 1,
                                "name": "Nik",
                                "middle_name": "0",
                                "surname": "Ivanov",
                                "phone": 375123456,
                                "email": "0",
                                "image_link": "http://jfnskjf",
                                "image_link_little": "http://sdfsfsdf",
                                "description": "0",
                                "lang": "ru",
                                "status": "active",
                                "last_active": 1688890372,
                                "create_date": 1688890372
                            }

                        }
                    },
                }
            }
        }
    },
    401: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": False,
                                  'description': 'Bad auth_id or access_token'}
                    },
                }
            }
        }
    },
}

get_users_by_contact_res = {
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": True,
                                  "user_list": ["user_object", "user_object", "user_object"],
                                  "phones_list": [43543543, 54363642345, 645746]
                                  }
                    },
                }
            }
        }
    },
    401: {
        "description": "Success",
        "content": {
            "application/json": {
                "examples": {
                    "odd": {
                        "summary": "Success",
                        "value": {"ok": False,
                                  'description': 'Bad auth_id or access_token'}
                    },
                }
            }
        }
    },
}
