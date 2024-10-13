from web.models import TechGroup


def create_groups():
    print("INFO: creating TechGroup entries")
    data_list = [
        {
            "name": "Business Brew",
            "icon": """<i class="fa-solid fa-mug-saucer"></i>""",
        },
        {
            "name": "Greater Spokane Inc",
            "icon": """""",
        },
        {
            "name": "Ignite Northwest",
            "icon": """""",
        },
        {
            "name": "INCH360",
            "icon": """""",
        },
        {
            "name": "SP3NW",
            "icon": """""",
        },
        {
            "name": "Spokane DevOps Meetup",
            "icon": """""",
        },
        {
            "name": "Spokane Go Users Group",
            "icon": """""",
        },
        {
            "name": "Spokane .NET Users Group",
            "icon": """""",
        },
        {
            "name": "spokaneOS",
            "icon": """""",
        },
        {
            "name": "Spokane Python User Group",
            "icon": """<i class="fa-brands fa-python"></i>""",
        },
        {
            "name": "Spokane Rust User Group",
            "icon": """""",
        },
        {
            "name": "Spokane Tech Community",
            "icon": """""",
        },
        {
            "name": "Spokane UX",
            "icon": """""",
        },
    ]
    for data in data_list:
        TechGroup.objects.get_or_create(name=data["name"], defaults=data)


def run():
    create_groups()
