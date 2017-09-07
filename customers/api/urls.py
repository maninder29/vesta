from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'fcm', FCMDeviceViewSet)
router.register(r'user', UserViewSet)
router.register(r'register', UserRegisterViewSet)
router.register(r'profile_register', ProfileRegisterViewSet)
# router.register(r'patient', PatientProfileViewset)
# router.register(r'clinic/slip', ClinicSlipViewSet)
# router.register(r'clinic/appointment', ClinicAppointmentViewSet)
# router.register(r'clinic/token', ClinicTokenStatusViewSet)
# router.register(r'lab/appointment', LabAppointmentViewSet)
# router.register(r'tests', TestViewSet)
# router.register(r'doctors', DoctorViewSet)
# router.register(r'clinics', ClinicViewSet)
# router.register(r'labs', LabViewSet)
# router.register(r'pharmacies', PharmacyViewSet)
# router.register(r'pharmacy/order', PharmacyOrderViewSet)
# router.register(r'bp', BloodPressureViewSet)
# router.register(r'sugar', SugarViewSet)
# router.register(r'cholesterol', CholesterolViewSet)
# router.register(r'temperature', TemperatureViewSet)
# router.register(r'bmi', BMIViewSet)

urlpatterns = router.urls