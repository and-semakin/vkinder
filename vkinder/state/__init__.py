import enum

from vkinder.state.hello import HelloAgainState, HelloErrorState, HelloState
from vkinder.state.initial import InitialState
from vkinder.state.list_matches import ListMatchesState
from vkinder.state.select_age import SelectAgeErrorState, SelectAgeState
from vkinder.state.select_city import SelectCityErrorState, SelectCityState
from vkinder.state.select_country import SelectCountryErrorState, SelectCountryState
from vkinder.state.select_sex import SelectSexErrorState, SelectSexState


class StateName(enum.Enum):
    # новый пользователь
    INITIAL = InitialState
    # приветствие
    HELLO = HelloState
    HELLO_ERROR = HelloErrorState
    HELLO_AGAIN = HelloAgainState
    # выбор страны
    SELECT_COUNTRY = SelectCountryState
    SELECT_COUNTRY_ERROR = SelectCountryErrorState
    # выбор города
    SELECT_CITY = SelectCityState
    SELECT_CITY_ERROR = SelectCityErrorState
    # выбор пола
    SELECT_SEX = SelectSexState
    SELECT_SEX_ERROR = SelectSexErrorState
    # выбор возраста
    SELECT_AGE = SelectAgeState
    SELECT_AGE_ERROR = SelectAgeErrorState
    # просмотр результатов поиска
    LIST_MATCHES = ListMatchesState


all_states = [state.value for state in StateName]

states = {state.key: state for state in all_states}
