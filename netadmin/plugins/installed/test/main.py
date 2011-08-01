from netadmin.plugins.core import Plugin

class TestPlugin(Plugin):
    
    _name = "Test plugin"
    
    def actions(self):
        return [
            ('event_field_list_item', self.event_field_list_item),
            ('event_field_list_value', self.event_field_list_value)
        ]
    
    def event_field_list_value(self, field_list_value):
        return "<strong>%s</strong>" % field_list_value
    
    def event_field_list_item(self, field_list_item):
        #return field_list_item.capitalize()
        return field_list_item
    
__plugins__ = [TestPlugin]