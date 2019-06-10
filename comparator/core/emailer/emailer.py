
from django.core.mail import EmailMessage

def send_email(email_id, max_error_count, project_name, scrapper_report, comparison_report):
    email_subject = 'Comparator Report: Immediate Comparison Report for {}'.format(project_name)
    email_body = '''
        Please check the report generated attached: \n
        Max Error Count: {}
    ''' .format(max_error_count)

    email_sender = 'rohanneps@gmail.com'
    email_receiver = [email_id]

    email_content = EmailMessage(
        email_subject,
        email_body,
        email_sender,
        email_receiver
    )

    email_content.attach_file(scrapper_report)
    email_content.attach_file (comparison_report)

    email_content.send()