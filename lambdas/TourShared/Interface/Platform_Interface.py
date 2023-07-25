from TourShared.Model.Data_Model import TourAvailabilityData, AppointmentData


class PlatformInterface:
    Body: {}
    Params: {}
    Headers: {}
    Error: {}

    def get_tour_schedule_request_data(self, appointment_data: AppointmentData, platform_data: dict):
        pass

    def get_tour_availability_request_data(self, availability_data: TourAvailabilityData, platform_data: dict):
        pass

    def format_tour_schedule_response(self, _data: dict):
        pass

    def format_tour_availability_response(self, _data: dict):
        pass
