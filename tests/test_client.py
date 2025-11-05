from unittest.mock import Mock, patch

import pytest

from esipie.client import BaseEsiClient


@pytest.fixture
def mock_operation():
    """Mock operation object."""
    op = Mock()
    op.parameters = [Mock(name='param1'), Mock(name='param2'), Mock(name='page')]
    op.parameters[0].name = 'param1'
    op.parameters[1].name = 'param2'
    op.parameters[2].name = 'page'
    op.tags = ['test_tag']
    op.operationId = 'test_operation'
    op.requestBody = True
    op.security = True
    return op


@pytest.fixture
def mock_api():
    """Mock OpenAPI instance."""
    api = Mock()
    request_mock = Mock()
    request_mock._process_request.return_value = ({'header1': 'value1'}, {'data': 'test'})
    api.createRequest.return_value = request_mock
    return api


@pytest.fixture
def mock_config():
    """Mock Config instance."""
    config = Mock()
    config.cache_prefix = 'test_prefix'
    config.cache_redis_url = 'redis://localhost:6379'
    return config


@pytest.fixture
def base_client(mock_operation, mock_api, mock_config):
    """BaseEsiClient instance with mocked dependencies."""
    operation_tuple = ('GET', 'https://api.example.com/test', mock_operation, None)
    with patch('esipie.client.Config', return_value=mock_config), \
         patch('esipie.client.redis.Redis.from_url') as mock_redis:
        mock_cache = Mock()
        mock_redis.return_value = mock_cache
        client = BaseEsiClient(operation_tuple, mock_api)
        client.cache = mock_cache
        return client


class TestBaseEsiClient:
    def test_init(self, base_client, mock_operation, mock_api, mock_config):
        """Test initialization of BaseEsiClient."""
        assert base_client.method == 'GET'
        assert base_client.url == 'https://api.example.com/test'
        assert base_client.operation == mock_operation
        assert base_client.extra is None
        assert base_client.api == mock_api
        assert base_client.token is None
        assert base_client.config == mock_config
        assert base_client._kwargs == {}

    def test_call(self, base_client):
        """Test __call__ method sets args and kwargs."""
        result = base_client('arg1', 'arg2', param1='value1', param2='value2')
        assert result == base_client
        assert base_client._args == ('arg1', 'arg2')
        assert base_client._kwargs == {'param1': 'value1', 'param2': 'value2'}

    def test_unnormalize_parameters_exact_match(self, base_client):
        """Test parameter normalization with exact matches."""
        params = {'param1': 'value1', 'unknown': 'value2'}
        result = base_client._unnormalize_parameters(params)
        assert result == {'param1': 'value1', 'unknown': 'value2'}

    def test_unnormalize_parameters_hyphen_variant(self, base_client):
        """Test parameter normalization with hyphen variants."""
        # Mock operation with hyphenated param
        base_client.operation.parameters = [Mock(name='param-name')]
        base_client.operation.parameters[0].name = 'param-name'

        params = {'param_name': 'value1'}
        result = base_client._unnormalize_parameters(params)
        assert result == {'param-name': 'value1'}

    def test_unnormalize_parameters_case_insensitive(self, base_client):
        """Test parameter normalization with case insensitive matches."""
        params = {'PARAM1': 'value1', 'Param2': 'value2'}
        result = base_client._unnormalize_parameters(params)
        assert result == {'param1': 'value1', 'param2': 'value2'}

    def test_unnormalize_parameters_no_parameters(self, base_client):
        """Test parameter normalization when operation has no parameters."""
        base_client.operation.parameters = []
        params = {'param1': 'value1'}
        result = base_client._unnormalize_parameters(params)
        assert result == {'param1': 'value1'}

    def test_unnormalize_parameters_exception_handling(self, base_client):
        """Test parameter normalization when accessing parameters raises exception."""
        with patch.object(base_client.operation, 'parameters', new_callable=lambda: Mock(side_effect=Exception)):
            params = {'param1': 'value1'}
            result = base_client._unnormalize_parameters(params)
            assert result == {'param1': 'value1'}

    def test_cache_key_generation(self, base_client):
        """Test cache key generation."""
        base_client._args = ('arg1',)
        base_client._kwargs = {'param1': 'value1', 'token': 'secret_token'}

        key = base_client._cache_key()
        assert key.startswith('test_prefix:')
        assert len(key) == len('test_prefix:') + 64  # prefix + 32-byte hex

    def test_etag_cache_key(self, base_client):
        """Test ETag cache key generation."""
        with patch.object(base_client, '_cache_key', return_value='base_key'):
            assert base_client._etag_cache_key() == 'base_key:etag'

    def test_data_cache_key(self, base_client):
        """Test data cache key generation."""
        with patch.object(base_client, '_cache_key', return_value='base_key'):
            assert base_client._data_cache_key() == 'base_key:data'

    def test_extract_body_params_with_body(self, base_client):
        """Test extracting body parameter when operation supports it."""
        base_client._kwargs = {'body': {'data': 'test'}, 'other': 'value'}
        result = base_client._extract_body_params()
        assert result == {'data': 'test'}
        assert 'body' not in base_client._kwargs
        assert base_client._kwargs == {'other': 'value'}

    def test_extract_body_params_no_body(self, base_client):
        """Test extracting body parameter when none provided."""
        base_client._kwargs = {'other': 'value'}
        result = base_client._extract_body_params()
        assert result is None
        assert base_client._kwargs == {'other': 'value'}

    def test_extract_body_params_unsupported_operation(self, base_client):
        """Test extracting body parameter when operation doesn't support it."""
        base_client.operation.requestBody = False
        base_client._kwargs = {'body': {'data': 'test'}}

        with pytest.raises(ValueError, match='This operation does not accept a body parameter'):
            base_client._extract_body_params()

    def test_extract_token_param_from_kwargs(self, base_client):
        """Test extracting token from kwargs."""
        base_client._kwargs = {'token': 'kw_token', 'other': 'value'}
        result = base_client._extract_token_param()
        assert result == 'kw_token'
        assert 'token' not in base_client._kwargs

    def test_extract_token_param_from_instance(self, base_client):
        """Test extracting token from instance when not in kwargs."""
        base_client.token = 'instance_token'
        base_client._kwargs = {'other': 'value'}
        result = base_client._extract_token_param()
        assert result == 'instance_token'

    def test_extract_token_param_instance_precedence(self, base_client):
        """Test that instance token takes precedence over kwargs."""
        base_client.token = 'instance_token'
        base_client._kwargs = {'token': 'kw_token'}
        result = base_client._extract_token_param()
        assert result == 'instance_token'

    def test_extract_token_param_unsupported_operation(self, base_client):
        """Test extracting token when operation doesn't support it."""
        base_client.operation.security = False
        base_client._kwargs = {'token': 'test_token'}

        with pytest.raises(ValueError, match='This operation does not accept a token parameter'):
            base_client._extract_token_param()

    def test_has_page_param_true(self, base_client):
        """Test _has_page_param returns True when page parameter exists."""
        assert base_client._has_page_param() is True

    def test_has_page_param_false(self, base_client):
        """Test _has_page_param returns False when page parameter doesn't exist."""
        base_client.operation.parameters = [Mock(name='param1'), Mock(name='param2')]
        base_client.operation.parameters[0].name = 'param1'
        base_client.operation.parameters[1].name = 'param2'
        assert base_client._has_page_param() is False

    def test_has_cursor_param_true_before(self, base_client):
        """Test _has_cursor_param returns True when 'before' parameter exists."""
        base_client.operation.parameters = [Mock(name='before')]
        base_client.operation.parameters[0].name = 'before'
        assert base_client._has_cursor_param() is True

    def test_has_cursor_param_true_after(self, base_client):
        """Test _has_cursor_param returns True when 'after' parameter exists."""
        base_client.operation.parameters = [Mock(name='after')]
        base_client.operation.parameters[0].name = 'after'
        assert base_client._has_cursor_param() is True

    def test_has_cursor_param_false(self, base_client):
        """Test _has_cursor_param returns False when neither before nor after exists."""
        base_client.operation.parameters = [Mock(name='param1')]
        base_client.operation.parameters[0].name = 'param1'
        assert base_client._has_cursor_param() is False

    def test_parse_cached_response(self, base_client, mock_api):
        """Test parsing cached response."""
        mock_response = Mock()
        result = base_client.parse_cached_response(mock_response)
        mock_api.createRequest.assert_called_once_with('test_tag.test_operation')
        mock_api.createRequest.return_value._process_request.assert_called_once_with(mock_response)
        assert result == ({'header1': 'value1'}, {'data': 'test'})

    def test_get_cache_hit_with_etag_match(self, base_client):
        """Test cache retrieval with ETag match."""
        cache_key = 'test_key'
        etag = 'test_etag'
        mock_cached_data = Mock()
        mock_cached_data.headers.get.return_value = etag

        base_client.cache.get.return_value = mock_cached_data
        with patch.object(
            base_client, 'parse_cached_response', return_value=({'header': 'value'}, 'data')
        ) as mock_parse:
            result = base_client._get_cache(cache_key, etag)
            assert result == ({'header': 'value'}, 'data', mock_cached_data)
            mock_parse.assert_called_once_with(mock_cached_data)

    def test_get_cache_hit_no_etag(self, base_client):
        """Test cache retrieval without ETag (should miss)."""
        cache_key = 'test_key'
        base_client.cache.get.return_value = Mock()

        result = base_client._get_cache(cache_key, None)
        assert result == (None, None, None)

    def test_get_cache_hit_etag_mismatch(self, base_client):
        """Test cache retrieval with ETag mismatch."""
        cache_key = 'test_key'
        etag = 'test_etag'
        mock_cached_data = Mock()
        mock_cached_data.headers.get.return_value = 'different_etag'

        base_client.cache.get.return_value = mock_cached_data

        result = base_client._get_cache(cache_key, etag)
        assert result == (None, None, None)

    def test_get_cache_miss(self, base_client):
        """Test cache miss."""
        cache_key = 'test_key'
        base_client.cache.get.return_value = None

        result = base_client._get_cache(cache_key, 'etag')
        assert result == (None, None, None)

    def test_get_cache_exception(self, base_client):
        """Test cache access exception handling."""
        cache_key = 'test_key'
        base_client.cache.get.side_effect = Exception('Cache error')

        with patch('esipie.client.logger') as mock_logger:
            result = base_client._get_cache(cache_key, 'etag')
            assert result == (None, None, None)
            mock_logger.warning.assert_called_once()