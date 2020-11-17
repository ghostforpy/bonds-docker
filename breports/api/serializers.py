from rest_framework import serializers
#from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from config.settings.base import APPS_DIR
from moex.api.serializers import SecurityRetrivieSerializer
from ..models import BReport

#from bonds.users.api.serializers import UserSerializer
# from moex.api.serializers import SecurityInPortfolioSerializer,\
#    TradeHistorySerializerForPortfolioDetail


class BReportUploadSerializer(serializers.ModelSerializer):

    class Meta:
        model = BReport
        exclude = ['created']
        read_only_fields = ['owner', 'filename', 'created']


class SimpleBReportUploadSerializer(serializers.Serializer):
    filename = serializers.FileField()

    def save(self):
        filename = self.validated_data['filename']
        fs = FileSystemStorage(location=APPS_DIR / 'broker_reports')
        saved_file = fs.save(filename.name, filename)
        return '{}/{}'.format(fs.location, saved_file), fs

    def validate(self, data):
        """
        Check that file size less than 2621440 bites(2.5 MB).
        """
        filename = data['filename']
        if filename.size > 2621440:
            raise serializers.ValidationError(
                "size must be less than 2621440 bites (2.5 MB)"
            )
        """
        Check that file is xls/xlsx.
        """
        if filename.name.split('.')[1] not in ['xls', 'xlsx',
                                               'XLS', 'XLSX']:
            raise serializers.ValidationError(
                "file must be xls/xlsx"
            )
        return data


class SecuritySerializer(SecurityRetrivieSerializer):

    class Meta(SecurityRetrivieSerializer.Meta):
        exclude = SecurityRetrivieSerializer.Meta.exclude + [
            'accint',
            'change_price_percent',
            'code',
            'coupondate',
            'couponfrequency',
            'couponpercent',
            'couponvalue',
            'created',
            'description',
            'facevalue',
            'fullname',
            'id',
            'initialfacevalue',
            'matdate',
            'name',
            'regnumber',
            'url',
            'users_follows'
        ]


class NonZeroSecuritySerializer(serializers.Serializer):
    count = serializers.DecimalField(
        max_digits=17,
        decimal_places=7
    )
    security = SecuritySerializer()
    total = serializers.DecimalField(
        max_digits=17,
        decimal_places=7
    )
    price_in_rub = serializers.DecimalField(
        max_digits=17,
        decimal_places=7
    )
    total_in_rub = serializers.DecimalField(
        max_digits=17,
        decimal_places=7
    )


class InvestsOperationSerializer(serializers.Serializer):
    cash = serializers.DecimalField(
        max_digits=17,
        decimal_places=2
    )
    cash_in_rub = serializers.DecimalField(
        max_digits=17,
        decimal_places=2
    )
    date = serializers.DateField()
    action = serializers.BooleanField()
    currency = serializers.CharField()


class SecuritySimpleSerializer(serializers.Serializer):
    isin = serializers.CharField()
    emitent = serializers.CharField()
    secid = serializers.CharField()
    facevalue = serializers.DecimalField(
        max_digits=17,
        decimal_places=7
    )
    faceunit = serializers.CharField(source='get_faceunit_display')
    security_type = serializers.CharField(
        source='get_security_type_display')
    name = serializers.CharField()


class SecurityTransactionSerializer(serializers.Serializer):
    deal_number = serializers.CharField()
    order_number = serializers.CharField()
    date = serializers.DateField()


class IncomeCertificateSecuritySerializer(serializers.Serializer):
    security = SecuritySimpleSerializer()
    count = serializers.DecimalField(
        max_digits=17,
        decimal_places=7
    )
    participation_basis = SecurityTransactionSerializer(many=True)


class ProfitSerializer(serializers.Serializer):
    value = serializers.DecimalField(
        max_digits=17,
        decimal_places=7
    )
    currency = serializers.CharField()


class ProfitSellSerializer(serializers.Serializer):
    security = SecuritySimpleSerializer()
    total_profit = serializers.DecimalField(
        max_digits=17,
        decimal_places=7
    )
    total_tax_base_without_commissions = serializers.DecimalField(
        max_digits=17,
        decimal_places=7
    )
    total_commissions = serializers.DecimalField(
        max_digits=17,
        decimal_places=7
    )
    total_tax_base = serializers.DecimalField(
        max_digits=17,
        decimal_places=7
    )
