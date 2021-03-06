import graphene
from graphene_django import DjangoObjectType
# from graphene_django.rest_framework.mutation import SerializerMutation
from .serializers import *
from .models import *
# from django.contrib.auth.mixins import LoginRequiredMixin

# from backend.api import serializers


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'is_staff', 'is_superuser', 'is_active', 'date_joined')


class WalletType(DjangoObjectType):
    class Meta:
        model = Wallet
        fields = ('id', 'user', 'currency', 'balance',
                  'created_at', 'updated_at', 'publickey')


class TransactionType(DjangoObjectType):
    class Meta:
        model = Transaction


class CurrencyType(DjangoObjectType):
    class Meta:
        model = Currency


class UpdateCurrencies(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        symbol = graphene.String()
        admin = graphene.Int()
        market_cap = graphene.Int()

    currency = graphene.Field(CurrencyType)

    def mutate(self, info, id, name=None, symbol=None, admin=None, market_cap=None, initial_balance=None):
        currency = Currency.objects.get(id=id)
        if info.context.user.is_authenticated and (info.context.user.is_superuser or currency.admin == info.context.user):
            if name:
                currency.name = name
            if symbol:
                currency.symbol = symbol
            if admin:
                currency.admin = User.objects.get(id=admin)
            if market_cap:
                currency.market_cap = market_cap
            if initial_balance:
                currency.initial_balance = initial_balance
            currency.save()
            return UpdateCurrencies(currency=currency)
        else:
            raise Exception('Not authorized')


class DeleteCurrencies(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id):
        currency = Currency.objects.get(id=id)
        # print(info.context.user)
        if info.context.user.is_authenticated and (info.context.user.is_superuser or currency.admin == info.context.user):
            currency.delete()
            return DeleteCurrencies(ok=True)
        return DeleteCurrencies(ok=False)


class Query(graphene.ObjectType):
    all_users = graphene.List(UserType, description="List of all users")
    user_by_id = graphene.Field(
        UserType, id=graphene.Int(), description="Get user by id")
    user_by_username = graphene.Field(
        UserType, username=graphene.String(), description="Get user by username")

    all_wallets = graphene.List(WalletType, description="List of all wallets")
    wallet_by_id = graphene.Field(
        WalletType, id=graphene.Int(), description="Get wallet by id")
    wallets_by_user = graphene.List(
        WalletType, user=graphene.String(), description="List of all wallets of a user")
    wallets_by_currency = graphene.List(WalletType,
                                        currency=graphene.String(), description="List of all wallets of a currency")

    all_transactions = graphene.List(
        TransactionType, description="List of all transactions")
    transaction_by_id = graphene.Field(
        TransactionType, id=graphene.Int(), description="Get transaction by id")
    transactions_by_sender = graphene.List(TransactionType, sender=graphene.String(
    ), description="List of all transactions of a sender")
    transactions_by_reciever = graphene.List(TransactionType, receiver=graphene.String(
    ), description="List of all transactions of a receiver")
    transactions_by_time_period = graphene.List(TransactionType, start_date=graphene.String(
    ), end_date=graphene.String(), description="List of all transactions between two dates")
    transactions_by_currency = graphene.List(TransactionType, currency=graphene.String(
    ), description="List of all transactions of a currency")

    all_currencies = graphene.List(
        CurrencyType, description="List of all currencies")
    currency_by_id = graphene.Field(
        CurrencyType, id=graphene.Int(), description="Get currency by id")
    currency_by_symbol = graphene.Field(
        CurrencyType, symbol=graphene.String(), description="Get currency by symbol")
    search_currencies_by_name = graphene.List(
        CurrencyType, name=graphene.String(), description="Search currencies by name")
    currency_by_invite_code = graphene.Field(
        CurrencyType, invite_code=graphene.String(), description="Get currency by invite code")
    currencies_by_admin = graphene.List(CurrencyType, admin=graphene.String(
    ), description="List of all currencies of a user")

    def resolve_all_users(self, info, **kwargs):
        return User.objects.all()

    def resolve_user_by_id(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return User.objects.get(pk=id)
        return None

    def resolve_user_by_username(self, info, **kwargs):
        username = kwargs.get('username')
        if username is not None:
            return User.objects.get(username=username)
        return None

    def resolve_all_wallets(self, info, **kwargs):
        return Wallet.objects.all()

    def resolve_wallet_by_id(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Wallet.objects.get(pk=id)
        return None

    def resolve_wallets_by_user(self, info, **kwargs):
        user = kwargs.get('user')
        if user is not None:
            return Wallet.objects.filter(user=user)
        return None

    def resolve_wallets_by_currency(self, info, **kwargs):
        currency = kwargs.get('currency')
        if currency is not None:
            return Wallet.objects.filter(currency=currency)
        return None

    def resolve_all_transactions(self, info, **kwargs):
        return Transaction.objects.all()

    def resolve_transaction_by_id(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Transaction.objects.get(pk=id)
        return None

    def resolve_transactions_by_sender(self, info, **kwargs):
        sender = kwargs.get('sender')
        if sender is not None:
            return Transaction.objects.filter(sender=sender)
        return None

    def resolve_transactions_by_reciever(self, info, **kwargs):
        receiver = kwargs.get('receiver')
        if receiver is not None:
            return Transaction.objects.filter(receiver=receiver)
        return None

    def resolve_transactions_by_time_period(self, info, **kwargs):
        """
        Description:
            Returns all transactions between two dates
        Example:
            {
                transactionsByTimePeriod(start_date: "2020-01-01", end_date: "2020-01-02"){
                    id
                    sender {
                        username
                    }
                }
            }
        """
        start_date = kwargs.get('start_date')
        end_date = kwargs.get('end_date')
        if start_date is not None and end_date is not None:
            return Transaction.objects.filter(created_at__range=[start_date, end_date])
        return None

    def resolve_transactions_by_currency(self, info, **kwargs):
        currency = kwargs.get('currency')
        if currency is not None:
            return Transaction.objects.filter(currency=currency)
        return None

    def resolve_all_currencies(self, info, **kwargs):
        return Currency.objects.all()

    def resolve_currency_by_id(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Currency.objects.get(pk=id)
        return None

    def resolve_currency_by_symbol(self, info, **kwargs):
        symbol = kwargs.get('symbol')
        if symbol is not None:
            return Currency.objects.get(symbol=symbol)
        return None

    def resolve_search_currencies_by_name(self, info, **kwargs):
        name = kwargs.get('name')
        if name is not None:
            return Currency.objects.filter(name__icontains=name)
        return None

    def resolve_currency_by_invite_code(self, info, **kwargs):
        invite_code = kwargs.get('invite_code')
        if invite_code is not None:
            return Currency.objects.get(invite_code=invite_code)
        return None

    def resolve_currencies_by_admin(self, info, **kwargs):
        admin = kwargs.get('admin')
        if admin is not None:
            return Currency.objects.filter(admin=admin)
        return None


class Mutation(graphene.ObjectType):
    update_currency = UpdateCurrencies.Field()
    delete_currency = DeleteCurrencies.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
