from app import db

# Class ranges are inclusive here
LEVELS_TO_CLASS_RANGES = {
    'חט"ב + עליונה': (7, 12),
    'חט"ב בלבד': (7, 8),
    'יסודי בלבד': (1, 6),
    'יסודי וחט"ב': (1, 8),
    'יסודי ועליונה': (1, 12),
    'יסודי חט"ב ועליונה': (1, 12),
    'עליונה בלבד': (9, 12)
}
RELIGIOUS_SCHOOLS_SUPERVISIONS = {'חרדי', 'ממלכתי דתי'}


class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    city = db.Column(db.String(30))
    supervision = db.Column(db.String(20))
    level = db.Column(db.String(20))
    is_approved = db.Column(db.Boolean)
    payments = db.relationship(
        'SchoolPayment', backref='school', lazy='dynamic')

    def has_class(self, class_id):
        class_range = LEVELS_TO_CLASS_RANGES[self.level]
        # range by default is exclusive, while our dict is inclusive, so +1
        return class_id in range(class_range[0], class_range[1] + 1)

    @property
    def is_religious(self):
        return self.supervision in RELIGIOUS_SCHOOLS_SUPERVISIONS

    def __repr__(self):
        return "School {}, {}, {}, {}, {}, {}".format(self.id, self.name, self.city, self.supervision,
                                                      self.level, self.is_approved)

    def __str__(self):
        return "{}, {}[{}]".format(self.name, self.city, self.level)


class SchoolPayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('school.id'))
    # Since class is a reserved python keyword, but actual column name is
    # `class`
    of_class = db.Column('class', db.Integer)
    clause = db.Column(db.String(100))
    type = db.Column(db.String(100))
    price = db.Column(db.Float)