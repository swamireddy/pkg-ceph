// -*- mode:C++; tab-width:8; c-basic-offset:2; indent-tabs-mode:t -*-
// vim: ts=8 sw=2 smarttab

#ifndef _INCLUDED_BOUNDED_BUFFER_HPP
#define _INCLUDED_BOUNDED_BUFFER_HPP

#include <boost/bind.hpp>
#include <boost/circular_buffer.hpp>
#include <boost/thread/condition.hpp>
#include <boost/thread/mutex.hpp>

// Taken from http://www.boost.org/doc/libs/1_55_0/libs/circular_buffer/example/circular_buffer_bound_example.cpp
template <class T>
class BoundedBuffer {
public:
  typedef boost::circular_buffer<T> container_type;
  typedef typename container_type::size_type size_type;
  typedef typename container_type::value_type value_type;
  typedef typename boost::call_traits<value_type>::param_type param_type;

  explicit BoundedBuffer(size_type capacity) : m_unread(0), m_container(capacity) {
  }

  void push_front(typename boost::call_traits<value_type>::param_type item) {
    // `param_type` represents the "best" way to pass a parameter of type `value_type` to a method.
    boost::mutex::scoped_lock lock(m_mutex);
    m_not_full.wait(lock, boost::bind(&BoundedBuffer<value_type>::is_not_full, this));
    m_container.push_front(item);
    ++m_unread;
    lock.unlock();
    m_not_empty.notify_one();
  }

  void pop_back(value_type* pItem) {
    boost::mutex::scoped_lock lock(m_mutex);
    m_not_empty.wait(lock, boost::bind(&BoundedBuffer<value_type>::is_not_empty, this));
    *pItem = m_container[--m_unread];
    lock.unlock();
    m_not_full.notify_one();
  }

private:
  BoundedBuffer(const BoundedBuffer&);             // Disabled copy constructor.
  BoundedBuffer& operator= (const BoundedBuffer&); // Disabled assign operator.

  bool is_not_empty() const {
    return m_unread > 0;
  }
  bool is_not_full() const {
    return m_unread < m_container.capacity();
  }

  size_type m_unread;
  container_type m_container;
  boost::mutex m_mutex;
  boost::condition m_not_empty;
  boost::condition m_not_full;
};

#endif
