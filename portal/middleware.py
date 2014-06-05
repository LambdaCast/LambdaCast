'''
Created on Jun 2, 2014

@author: benjamin
'''

from portal.models import Submittal

class SubmittalMiddleware(object):

    def process_template_response(self, request, response):
        ''' add submittals to response context '''

        user = request.user
        response.context_data['submittal_list'] = Submittal.objects.filter(users=user) if user.is_authenticated() else []

        return response