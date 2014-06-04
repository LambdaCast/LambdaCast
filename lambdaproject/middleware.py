'''
Created on Jun 4, 2014

@author: benjamin
'''

import settings

class SettingsMiddleware(object):

    def process_template_response(self, request, response):
        ''' add settings to response context '''
        context = response.context_data

        if 'settings' not in context:
            context['settings'] = settings

        return response