from src.domain.main.ExternalServices.Payment.PaymentServices import IPaymentService, PaymentService
from src.domain.main.ExternalServices.Payment.ExternalPaymentServices import ExternalPaymentServiceReal

from src.domain.main.ExternalServices.Provision.IProvisionService import provisionReal

from src.domain.main.ExternalServices.Provision.ProvisionServiceAdapter import provisionService


def init_external_services_from_configuration(base_url):
    external_payment_service_real = ExternalPaymentServiceReal(base_url)
    payment_service = PaymentService(external_payment_service_real)
    provision_service = provisionReal(base_url)
    provision_service_adapter = provisionService(provision_service)
    return payment_service, provision_service_adapter
