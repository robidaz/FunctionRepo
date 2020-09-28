import random
from retrying import Retrying
from myfunctions.dictmods import filter_dict
import smtplib
import cx_Oracle
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from os.path import basename
from myfunctions.listmods import to_list
        
def unreliable_function(self, failure_ratio=.5):
    failure_ratio = float(failure_ratio)
    if failure_ratio >= 1:
        raise AssertionError("Percentage must be given as decimal")
    failure_ratio = round(failure_ratio, 2)
    random_number = random.randint(0, 100)
    try:
        assert random_number < (failure_ratio * 100)
    except AssertionError:
        raise AssertionError("Function was unreliable and failed")
    print("Function Passed")
    
def retry_on_failure(target_function, *args, **kwargs):
    """
     This method allows a function to be called and retried
    upon failure. This method uses the Retrying object from the
    retrying package which has a number of parameters that can be passed
    in as a kwarg. The kwargs are filtered to the proper function they
    belong to. Ensure that your target function does not use any of the
    same parameters as the retrying function (shown below). ALL TIME RELATED
    PARAMETERS ARE IN milliseconds

    :param target_function: The function to retry
    :param args: The functions arguments

    --optional params for the Retrying object--

    :param stop=None
    :param wait=None
    :param stop_max_attempt_number=None
    :param stop_max_delay=None
    :param wait_incrementing_start=None
    :param wait_incrementing_increment=None
    :param wait_fixed=None
    :param wait_random_min=None
    :param wait_random_max=None
    :param wait_exponential_multiplier=None
    :param wait_exponential_max=None
    :param retry_on_exception=None
    :param retry_on_result=None
    :param wrap_exception=False
    :param stop_func=None
    :param wait_func=None
    :param wait_jitter_max=None
    """
    try:
        for potential_key in [
            'stop_max_delay',
            'wait_incrementing_start',
            ' wait_incrementing_increment',
            'wait_fixed',
            'wait_random_min',
            'wait_random_max',
            'wait_exponential_max',
                'wait_jitter_max']:
            kwargs[potential_key] = int(round(kwargs[potential_key] * 1000))
    except KeyError:
        pass
    try:
        kwargs['wait_exponential_max']
    except KeyError:
        try:
            # cut the max delay at 5% of the total time to increase attempts
            kwargs['wait_exponential_max'] = kwargs['stop_max_delay'] * .05
        except KeyError:
            pass
    target_function_kwargs = filter_dict(kwargs, target_function)
    return Retrying(**kwargs).call(target_function,
                                   *args, **target_function_kwargs)
    
    
def send_email(smtp_string, sender, recipients,
               subject, body, paths_to_attachment=None):
    recipients = recipients.split(';')
    if recipients[-1] == [' '] or recipients[-1] == []:
        recipients = recipients[:-1]
    if len(subject) > 100:
        raise ValueError("Subject must be under 100 characters")
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    if paths_to_attachment is None:
        paths_to_attachment = []
    else:
        paths_to_attachment = to_list(paths_to_attachment)
    for path_to_attachment in paths_to_attachment:
        filename = basename(path_to_attachment)
        attachment = open(path_to_attachment, "rb")
        p = MIMEBase('application', 'octet-stream')
        p.set_payload((attachment).read())
        encoders.encode_base64(p)
        p.add_header(
            'Content-Disposition',
            "attachment; filename= %s" %
            filename)
        msg.attach(p)
    address, port = smtp_string.split(':')
    s = smtplib.SMTP(address, port)
    text = msg.as_string()
    s.sendmail(sender, recipients, text)
    s.quit()
    
def run_query(sql, querytype='Value', DB_USERNAME='', DB_PASSWORD='', DB_CONNECTIONSTRING=''):  # pylint: disable=invalid-name
    '''
    Function used to make queries. Note all Tables must be prefixed with SCHEMA (ex: WM19.ASN)
    :param DB_USERNAME: Database Username
    :param DB_PASSWORD: Database Password
    :param DB_CONNECTIONSTRING: Database connection string in the form: hostname:port/service_name
    '''
    if not DB_USERNAME or not DB_PASSWORD or not DB_CONNECTIONSTRING:
        raise ValueError('DB Parameters cannot be empty')
    if not querytype in ('Value', 'Random', 'List'):
        raise ValueError(f'{querytype} is not a supported query type')
    conn = None
    try:
        conn = cx_Oracle.connect(
            f"{DB_USERNAME}/{DB_PASSWORD}@{DB_CONNECTIONSTRING}")

        try:
            curs = conn.cursor()
            curs.execute(sql)
            query_list = [i[0] for i in curs.fetchall()]
            if query_list == []:
                return 'Null'
            if querytype == 'Value':
                return query_list[0]
            if querytype == 'Random':
                return random.choice(query_list)
            if querytype == 'List':
                return query_list
        finally:
            curs.close()
    finally:
        if conn is not None:
            conn.close()