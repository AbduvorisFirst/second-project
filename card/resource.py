from import_export.resources import ModelResource
from .models import Card

class CardRecource(ModelResource):
    class Meta:
        model = Card
        fields = ['card_number','expire','phone','status','balance']
        import_id_fields = ['card_number']   
        
    def before_import(self, dataset, **kwargs):
        # header qatorni topish
        for i, row in enumerate(dataset):
            if 'card_number' in row:
                dataset.headers = row
                dataset._data = dataset._data[i+1:]
                break