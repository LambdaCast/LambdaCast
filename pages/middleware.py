'''
Created on Jun 4, 2014

@author: benjamin
'''

from pages.models import Page

class PagesMiddleware(object):

    def process_template_response(self, request, response):
        ''' add pages to response context '''

        response.context_data['page_list'] = Page.objects.filter(activated=True).order_by('orderid')

        return response