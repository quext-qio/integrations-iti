from sqlalchemy import and_, desc

from DatabaseConnection.db_connector import DBConnection
from Models.ips_models import PartnerEndpoint, Communities, PartnerCommunity, PartnerSystem, PartnerCommunityPurpose, \
    Purpose, PartnerEnvironment, PartnerVersion, Partner, Category, PartnerCommunityPurposeEndpoint

session = DBConnection().get_db_session()


class EndpointHandler:
    """
    Class to handle API endpoints.

    This class provides methods to retrieve API information from the database.

    """

    @staticmethod
    def get_api_info(request_data):
        """
        Retrieves API information based on the provided request data.

        Args:
            request_data: Data used to query API information.

        Returns:
            list: A list of API endpoint data retrieved from the database.
        """
        end_point_data = (
            session.query(Communities)
            .join(PartnerCommunity, PartnerCommunity.community_id == Communities.community_id)
            .join(Category, Category.category_name == request_data.category_name)
            .join(Partner, Partner.partner_id == PartnerCommunity.partner_id)
            .join(Purpose, Purpose.purpose_name == request_data.purpose_name)
            .join(
                PartnerSystem,
                PartnerSystem.partner_id == PartnerCommunity.partner_id
            )
            .join(
                PartnerCommunityPurpose,
                and_(
                    PartnerCommunityPurpose.partner_community_id == PartnerCommunity.partner_community_id,
                    PartnerCommunityPurpose.purpose_id == Purpose.purpose_id
                )
            )
            .join(
                PartnerEnvironment,
                and_(
                    PartnerEnvironment.partner_id == PartnerCommunity.partner_id,
                    PartnerEnvironment.partner_system_id == PartnerSystem.partner_system_id
                )
            )
            .join(
                PartnerVersion,
                and_(
                    PartnerVersion.partner_id == PartnerCommunity.partner_id,
                    PartnerVersion.partner_system_id == PartnerSystem.partner_system_id,
                    PartnerVersion.partner_environment_id == PartnerEnvironment.partner_environment_id
                )
            )
            .join(
                PartnerCommunityPurposeEndpoint,
                and_(
                    PartnerCommunityPurposeEndpoint.category_id == Category.category_id,
                    PartnerCommunityPurposeEndpoint.partner_community_id == PartnerCommunity.partner_community_id,
                    PartnerCommunityPurposeEndpoint.purpose_id == Purpose.purpose_id
                )
            )
            .join(
                PartnerEndpoint,
                and_(
                    PartnerEndpoint.partner_id == PartnerCommunity.partner_id,
                    PartnerEndpoint.partner_version_id == PartnerVersion.partner_version_id,
                    PartnerEndpoint.partner_environment_id == PartnerEnvironment.partner_environment_id,
                    PartnerEndpoint.partner_system_id == PartnerSystem.partner_system_id,
                    PartnerEndpoint.partner_endpoint_id == PartnerCommunityPurposeEndpoint.partner_endpoint_id
                )
            )
            .filter(Communities.community_id == request_data.community_id)
            .with_entities(
                Partner.partner_code,
                PartnerEndpoint.partner_endpoint_id,
                PartnerEndpoint.host_name,
                PartnerEndpoint.protocol,
                PartnerEndpoint.request_method,
                PartnerEndpoint.url_path,
                PartnerEndpoint.endpoint_name,
                PartnerEndpoint.headers,
                PartnerEndpoint.template,
                PartnerEndpoint.related_endpoint_id
            )
            .order_by(desc(PartnerEndpoint.related_endpoint_id))
            .all()
        )

        return end_point_data

