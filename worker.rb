#!/usr/bin/env ruby

require 'json'
require 'redis'
require 'rest-client'
require 'logger'

# Ruby Logger with an ISO-8601 timestamp
class IsoLogger < Logger
  def initialize(logdev)
    super

    self.formatter = proc do |severity, datetime, _progname, msg|
      "#{datetime.utc.strftime('%FT%T.%L%z')} [#{severity}] #{msg}\n"
    end
  end
end

logger = IsoLogger.new(STDOUT)
RestClient.log = logger

redis = Redis.new(host: 'redis-msg.cdje8j.ng.0001.euc1.cache.amazonaws.com')
ready_messages_key = "complete"

loop do
  logger.info "Waiting for a key in #{ready_messages_key}"
  ready_message_key = redis.blpop(ready_messages_key).last
  logger.info "Got key #{ready_message_key}"

  parts = []
  part = redis.lpop(ready_message_key)
  until part.nil?
    parts << JSON.parse(part)
    part = redis.lpop(ready_message_key)
  end

  logger.info parts

  payload = parts.sort_by { |p| p["PartNumber"] }.map { |p| p["Data"] }.join

  url = "https://dashboard.cash4code.net/score/#{parts.first['Id']}"
  RestClient.post(
    url,
    payload,
    'x-gameday-token' => '4c01001182'
  )
end
