from app import create_app, db
from app.models import Tag

# create the app
app = create_app()
# create the database
with app.app_context():
    # define the tags to be added
    tags = [
        {"name": "Python", "description": "Python programming language"},
        {"name": "JavaScript",
         "description": "JavaScript programming language"},
        {"name": "Machine Learning",
         "description": "Courses about machine learning"},
        {"name": "Art", "description": "Courses about art"},
        {"name": "Music", "description": "Courses about music"}
    ]

    for tag_data in tags:
        # check if the tag already exists
        existing_tag = Tag.query.filter_by(name=tag_data["name"]).first()
        if not existing_tag:
            # if the tag does not exist, create a new tag
            new_tag = Tag(name=tag_data["name"],
                          description=tag_data["description"])
            db.session.add(new_tag)

    db.session.commit()
    print("Tags added to database!")
