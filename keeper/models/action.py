from datetime import datetime


class Action:
    """Class representing an Action."""
    def __init__(
        self, id, name, timestamp=datetime.now(), tags=[], activity_id=None, **kwargs
    ):
        self.id = id
        self.name = name
        self.timestamp = timestamp
        self.tags = tags
        self.activity_id = activity_id
        super().__init__(**kwargs)

    def __repr__(self):
        return (
            f"Action(id={self.id}, name={self.name}, timestamp={self.timestamp}, "
            f"tags={self.tags}, activity_id={self.activity_id})"
        )
