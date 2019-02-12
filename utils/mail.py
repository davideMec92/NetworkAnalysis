import smtplib

def sendMailToDavide( Text ):

  from_addr = "davidemaccarrone@ticketsms.it"
  to = "davide.nunzio.maccarrone@gmail.com"
  cc = ""
  subject = "Elaborazione Dati Network Analysis Terminata"
  message = "Elaborazione Dati Network Analysis Terminata"
  login = "davidemaccarrone@ticketsms.it"
  password = "ferdinandea1992!"
  smtpserver = "mail.ticketsms.it:587"

  header  = "From: " + str(from_addr) + "\n"
  header += "To: " + str(to) + "\n"
  header += "Subject: " + str(subject) + " \n"

  message = header + Text
  server = smtplib.SMTP(smtpserver)
  server.starttls()
  server.login(login,password)
  problems = server.sendmail(from_addr, to, message)
  server.quit()