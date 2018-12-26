import sys, getopt, subprocess
import boto3
import configparser

config = configparser.ConfigParser()
config.read('mfa.config')


def main(argv):
    mfa = config['mfa']
    profile = mfa.get('profile', 'default')
    session = boto3.session.Session(profile_name=profile)
    sts = session.client('sts')

    token = mfa.get('token')
    expiration = mfa.getint('expiration', 3600)
    serial_number = mfa.get('serial_number')
    try:
        opts, args = getopt.getopt(argv, "p:t:exp:")
    except getopt.GetoptError:
        print('mfa.py -t <mfa_token>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-p':
            profile = arg
        elif opt == '-t':
            token = arg
        elif opt == '-exp':
            expiration = arg
    if not (token and serial_number):
        raise ValueError('Missing token or serial_number parameters')
    credentials = sts.get_session_token(
        DurationSeconds=expiration,
        SerialNumber=serial_number,
        TokenCode=token)['Credentials']
    mfa_profile = profile + '-mfa'
    configure_profile(mfa_profile, 'aws_access_key_id', credentials['AccessKeyId'])
    configure_profile(mfa_profile, 'aws_secret_access_key', credentials['SecretAccessKey'])
    configure_profile(mfa_profile, 'aws_session_token', credentials['SessionToken'])


configure_command = 'aws configure set profile.'


def configure_profile(mfa_profile, param, value):
    command = configure_command + mfa_profile + '.' + param + ' ' + value
    subprocess.run(command, shell=True)
    print(command, ' Done')


if __name__ == "__main__":
    main(sys.argv[1:])
